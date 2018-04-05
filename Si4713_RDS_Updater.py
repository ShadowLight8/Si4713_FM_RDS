#!/usr/bin/python2.7

from sys import argv
from time import sleep
from datetime import datetime
from Adafruit_Si4713 import Adafruit_Si4713
import logging
import json
import os
import errno
import atexit
import socket

script_dir = os.path.dirname(os.path.abspath(argv[0]))

logging.basicConfig(filename=os.path.dirname(os.path.abspath(argv[0]))+'/Si4713_RDS_Updater.log',level=logging.INFO,format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
logging.info("----------")

fifo_path = script_dir + "/Si4713_FM_RDS_FIFO"

inited = False
stationdata = ' Happy  Hallo-     -ween'
stationfragments = (len(stationdata)-1)//8+1
stationdelay = 4
title = ''
artist = ''
bufferdelay = 6
showartist = True

# Establish lock via socket or exit if failed
try:
	lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
	lock_socket.bind('\0Si4713_RDS_Updater')
	logging.debug('Lock created')
except:
	logging.error('Unable to create lock. Another instance of Si4713_RDS_Updater.py running?')
	exit(-1)

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

try:
	logging.debug("Setting up read side of fifo " + fifo_path)
	os.mkfifo(fifo_path)
except OSError as oe:
	if oe.errno != errno.EEXIST:
		raise

with open(fifo_path, 'r', 0) as fifo:
	radio = Adafruit_Si4713()
	stationtick = 0
	stationfrag = 0
	buffertick = 0
	while True:
		line = fifo.readline().rstrip()
		if len(line) > 0:
			logging.debug('line - ' + line)
			if line == 'EXIT':
				logging.info('exit')
				exit()
			elif line == 'INIT':
				logging.info('init')
				# TODO: Reset Si4713, configure FM, configure blank RDS
				if not radio.begin():
					logging.error('Unable to initialize radio. Check that the Si4713 is connected, then restart FPPD.')
					exit(-1)
				radio.setTXpower(100)
				radio.tuneFM(10010)
				radio.beginRDS()
				radio.setRDSstation(stationdata[0:8])
				inited = True
				logging.info('Radio initialized')
			elif line == 'START':
				logging.info('start')
				# TODO: ?
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