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

class RDSBuffer(object):
	data = ''
	fragments = 0
	frag = 0
	delay = 0
	tick = 0

	def __init__(self, data='', fragsize=8, delay=5):
		self.data = data
		self.fragsize = fragsize
		self.fragments = (len(self.data)-1)//self.fragsize+1 #Private function on data changes?
		self.frag = 0
		self.delay = delay
		self.tick = 0

	def updateData(self, data):
		self.data = data
		updateFragments() # TODO: Check syntax
		self.frag = 0
		self.tick = 0

	def updateFragments(self): # TODO: Make private?
		self.fragments = (len(self.data)-1)//self.fragsize+1

	def nextTick():
		# Inc tick, return True if delay reached

	def nextFrag():
		# Inc frag, return Next fragment



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

# *_data: Complete string of all data to be sent
# *_fragments: How many block of 8 or 32 characters the *_data is
# *_frag: Current fragment being sent by radio
# *_delay: Time, in seconds, between frag updates
# *_tick: Counter to track time until next delay interval reached

#Make station and buffer a common class

station_data = ' Happy  Hallo-     -ween'
station_fragments = (len(stationdata)-1)//8+1
station_frag = 0
station_delay = 4
station_tick = 0

showartist = True # Should be removed
title = ''
artist = ''
track = ''
buffer_data = ''
buffer_fragments = 3
buffer_frag = 0
buffer_delay = 6
buffer_tick = 0

# Establish lock via socket or exit if failed
try:
	lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
	lock_socket.bind('\0Si4713_RDS_Updater')
	logging.debug('Lock created')
except:
	logging.error('Unable to create lock. Another instance of Si4713_RDS_Updater.py running?')
	exit(1)

# Config from os.path.abspath(argv[0])
# ../../config/plugin.Si4713_FM_RDS
# TODO: Not sure this is the right way to locate the config file, but it works

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
	if not radio.begin():
		logging.error('Unable to initialize radio. Check that the Si4713 is connected, then restart FPPD.')
		exit(1)
	radio.setTXpower(int(config['Power']))
	radio.tuneFM(int(config['Frequency'].replace('.','')))
	# TODO: If RDS enabled
	radio.beginRDS()
	radio.setRDSstation(stationdata[0:8])
	radio_ready = True
	logging.info('Radio initialized')

with open(fifo_path, 'r', 0) as fifo:
	while True:
		line = fifo.readline().rstrip()
		if len(line) > 0:
			logging.debug('line - %s', line)
			if line == 'EXIT':
				logging.info('exit')
				exit()

			elif line == 'RESET':
				config = read_config()
				radio = None
				radio = Adafruit_Si4713(resetpin = int(config['GPIONumReset']))
				radio.reset()
				radio_ready = False
				print ('GPIO Number %s reset', config['GPIONumReset'])

			elif line == 'INIT':
				logging.info('init')
				if config['Start'] == "FPPDStart":
					Si4713_start()

			elif line == 'START':
				logging.info('start')
				if config['Start'] == "Playlist":
					Si4713_start()

			elif line == 'STOP':
				logging.info('stop')
				if config['Stop'] == "Playlist":
					radio.reset()
					radio = None
					radio_ready = False
					logging.info('Radio stopped')

			elif line[0] == 'T':
				logging.debug('T')
				title = line[1:33]
				# Reset RDS buffer and tick to update when title changes
				logging.info('Reset buffer to title [' + title + ']')
				radio.setRDSbuffer(title)
				buffertick = 0

			elif line[0] == 'A':
				logging.debug('A')
				artist = line[1:33]

			else:
				# TODO: ?
				logging.info('else')

		else:
			stationtick = (stationtick + 1) % stationdelay
			if radio_ready and stationtick == 0:
				logging.info('Set station to fragment ' + str(stationfrag) + ' [' + stationdata[8*stationfrag:8*(stationfrag+1)] + ']')
				radio.setRDSstation(stationdata[8*stationfrag:8*(stationfrag+1)])
				stationfrag = (stationfrag + 1) % stationfragments

			buffertick = (buffertick + 1) % bufferdelay
			if radio_ready and buffertick == 0:
				if showartist:
					logging.info('Set buffer to artist [' + artist + ']')
					radio.setRDSbuffer(artist)
				else:
					logging.info('Set buffer to title [' + title + ']')
					radio.setRDSbuffer(title)
				showartist = not showartist

			# Sleep until the top of the next second
			sleep ((1000000 - datetime.now().microsecond) / 1000000.0)
