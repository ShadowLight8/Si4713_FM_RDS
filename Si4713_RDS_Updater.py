#!/usr/bin/python

import logging
import json
import os
import errno
import atexit
import socket
from sys import argv
from time import sleep
from datetime import datetime
from Adafruit_Si4713 import Adafruit_Si4713

class RadioBuffer(object):
# fragsize: How long the block from data will be. Likely 8 or 32
# delay: Time, in seconds, between frag updates
# data: Complete string of all data to be sent
# fragments: How many block of 8 or 32 characters the data is
# frag: Current fragment to be sent by radio
# tick: Counter to track time until next delay interval reached

	def __init__(self, data='', fragsize=8, delay=5):
		self.fragsize = fragsize
		self.delay = delay
		self.updateData(data)

	def updateData(self, data):
		self.data = data.ljust(self.fragsize) # Ensure at least one fragment
		self.__fragments = (len(self.data) - 1) // self.fragsize + 1
		self.__tick = self.delay - 1 # Setup nextTick to return true
		self.__frag = self.__fragments - 1 # Setup currentFragment to start at the beginning

	def currentFragment(self):
		return (self.data[self.fragsize * self.__frag:self.fragsize * (self.__frag + 1)]).ljust(self.fragsize)

	def nextTick(self):
		self.__tick = (self.__tick + 1) % self.delay
		if self.__tick == 0:
			self.__frag = (self.__frag + 1) % self.__fragments
			return True
		return False

script_dir = os.path.dirname(os.path.abspath(argv[0]))

logging.basicConfig(filename=script_dir + '/Si4713_updater.log', level=logging.DEBUG, format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
logging.info("----------")

def read_config():
	configfile = os.getenv('CFGDIR', '/home/fpp/media/config') + '/plugin.Si4713_FM_RDS'
	config = {}
	with open(configfile, 'r') as f:
        	for line in f:
                	(key, val) = line.split(' = ')
	                config[key] = val.replace('"', '').strip()
	logging.debug('Config %s', config)
	return config

config = read_config()

radio_ready = False

RDSStation = RadioBuffer(config['StationText'], 8, int(config['StationDelay']))
RDSText = RadioBuffer(config['RDSTextText'], 32, int(config['RDSTextDelay']))

title = ''
artist = ''
track = ''

# Establish lock via socket or exit if failed
try:
	lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
	lock_socket.bind('\0Si4713_RDS_Updater')
	logging.debug('Lock created')
except:
	logging.error('Unable to create lock. Another instance of Si4713_RDS_Updater.py running?')
	exit(1)

@atexit.register
def cleanup():
	try:
		logging.debug('Cleaning up fifo')
		os.unlink(fifo_path)
	except:
		pass

fifo_path = script_dir + "/Si4713_FM_RDS_FIFO"
try:
	logging.debug('Setting up read side of fifo %s', fifo_path)
	os.mkfifo(fifo_path)
except OSError as oe:
	if oe.errno != errno.EEXIST:
		raise
	else:
		logging.debug('Fifo already exists')

radio = Adafruit_Si4713(resetpin = int(config['GPIONumReset']))

def Si4713_start():
	logging.info('Si4713 Start')
	if config['Premphasis'] == '50us':
		radio.preemphasis = 1

	if not radio.begin():
		logging.error('Unable to initialize radio. Check that the Si4713 is connected, then restart FPPD.')
		exit(1)
	radio.setTXpower(int(config['Power']), int(config['AntCap']))
	radio.tuneFM(int(config['Frequency'].replace('.','')))
	# TODO: If RDS enabled
	if config['EnableRDS'] == True:
		radio.beginRDS()
		radio.setRDSstation(RDSStation.currentFragment())
	radio_ready = True
	logging.info('Radio initialized')

def updateRDSData():
	logging.info('Updating RDS Data')
	# TODO: Deal with different RDS options
	# TODO: RDSStation.updateData...
	RDSText.updateData('%s%s', title, artist)

with open(fifo_path, 'r', 0) as fifo:
	while True:
		line = fifo.readline().rstrip()
		if len(line) > 0:
			if line == 'EXIT':
				logging.info('Processing exit')
				# TODO: Should radio stop?
				exit()

			elif line == 'RESET':
				logging.info('Processing reset')
				config = read_config()
				radio = None
				radio = Adafruit_Si4713(resetpin = int(config['GPIONumReset']))
				radio.reset()
				radio_ready = False
				if config['Start'] == "FPPDStart":
					Si4713_start()

			elif line == 'INIT':
				logging.info('Processing init')
				if config['Start'] == "FPPDStart":
					Si4713_start()

			elif line == 'START':
				logging.info('Processing start')
				if config['Start'] == "Playlist":
					Si4713_start()

			elif line == 'STOP':
				logging.info('Processing stop')
				if config['Stop'] == "Playlist":
					radio.reset()
					radio = None
					radio_ready = False
					logging.info('Radio stopped')

			elif line[0] == 'T':
				logging.debug('Processing title')
				# TODO: Only use title if not blank
				title = line[1:33].ljust(32)
				updateRDSData()

			elif line[0] == 'A':
				logging.debug('Processing artist')
				artist = line[1:33].ljust(32)
				updateRDSData()

			elif line[0] == 'N':
				logging.debug('Processing track number')
				# TODO: Handle track number suffix " of 4" here?
				track = line[1:33].ljust(32)
				updateRDSData()

			else:
				logging.error('Unknown fifo input %s', line)

		else:
			if RDSStation.nextTick():
				logging.debug('Station Fragment [%s]', RDSStation.currentFragment())
				radio.setRDSstation(RDSStation.currentFragment())
			if RDSText.nextTick():
				logging.debug('Buffer Fragment  [%s]', RDSText.currentFragment())
				radio.setRDSbuffer(RDSText.currentFragment())

			# Sleep until the top of the next second
			sleep ((1000000 - datetime.now().microsecond) / 1000000.0)
