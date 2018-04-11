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

script_dir = os.path.dirname(os.path.abspath(argv[0]))

logging.basicConfig(filename=script_dir + '/Si4713_Updater.log', level=logging.DEBUG, format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
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

inited = False
stationdata = ' Happy  Hallo-     -ween'
stationfragments = (len(stationdata)-1)//8+1
stationdelay = 4
stationtick = 0
stationcurfrag = 0
showartist = True

title = ''
artist = ''
track = ''
bufferdata = ''
bufferfragments = 3
bufferdelay = 6
buffertick = 0
buffercurfrag = 0

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

def Si4713_start:
	logging.info('Si4713 Start')
	if not radio.begin():
		logging.error('Unable to initialize radio. Check that the Si4713 is connected, then restart FPPD.')
		exit(1)
	radio.setTXpower(int(config['Power']))
	radio.tuneFM(int(config['Frequency'].replace('.',''))
	# TODO: If RDS enabled
	radio.beginRDS()
	radio.setRDSstation(stationdata[0:8])
	inited = True
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
				inited = False
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
					inited = False
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
			if inited and stationtick == 0:
				logging.info('Set station to fragment ' + str(stationfrag) + ' [' + stationdata[8*stationfrag:8*(stationfrag+1)] + ']')
				radio.setRDSstation(stationdata[8*stationfrag:8*(stationfrag+1)])
				stationfrag = (stationfrag + 1) % stationfragments

			buffertick = (buffertick + 1) % bufferdelay
			if inited and buffertick == 0:
				if showartist:
					logging.info('Set buffer to artist [' + artist + ']')
					radio.setRDSbuffer(artist)
				else:
					logging.info('Set buffer to title [' + title + ']')
					radio.setRDSbuffer(title)
				showartist = not showartist

			# Sleep until the top of the next second
			sleep ((1000000 - datetime.now().microsecond) / 1000000.0)
