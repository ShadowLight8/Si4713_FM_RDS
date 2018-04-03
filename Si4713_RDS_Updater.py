#!/usr/bin/python2.7

from sys import argv
from time import sleep
from datetime import datetime
import logging
import json
import os
import errno
import atexit
import socket

script_dir = os.path.dirname(os.path.abspath(argv[0]))

logging.basicConfig(filename=os.path.dirname(os.path.abspath(argv[0]))+'/Si4713_RDS_Updater.log',level=logging.DEBUG,format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
logging.debug("----------")
logging.debug("Arguments %s", argv[1:])

fifo_path = script_dir + "/Si4713_FM_RDS_FIFO"
updater_name = "Si4713_RDS_Updater.py"

title = ''
artist = ''

# Establish lock via socket
lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
lock_socket.bind('\0Si4713_RDS_Updater')

# Config from os.path.abspath(argv[0])
# ../../config/plugin.Si4713_FM_RDS
# TODO: Not sure this is the right way to locate the config file, but it works

@atexit.register
def cleanup():
	try:
		os.unlink(fifo_path)
	except:
		pass

try:
	os.mkfifo(fifo_path)
except OSError as oe:
	if oe.errno != errno.EEXIST:
		raise

with open(fifo_path, 'r', 0) as fifo:
	while True:
		line = fifo.readline()
		line = line.rstrip()
		if len(line) > 0:
			logging.debug('line - ' + line)
			if line == 'EXIT':
				logging.debug('exit')
				exit()
			elif line == 'INIT':
				logging.debug('init')
				# TODO: Reset Si4713, configure FM, configure blank RDS
			elif line == 'START':
				logging.debug('start')
				# TODO: ?
			elif line[0] == 'T':
				logging.debug('T')
				title = line[1:33]
			elif line[0] == 'A':
				logging.debug('A')
				artist = line[1:33]
			else:
				# TODO: ?
				logging.debug('else')				
		else:
			if len(title) > 0:
				logging.debug('T-' + title)
			if len(artist) > 0:
				logging.debug('A-' + artist)
			# Sleep until the top of the next second
			sleep ((1000000 - datetime.now().microsecond) / 1000000.0)
