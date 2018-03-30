#!/usr/bin/env python

from sys import argv
from time import sleep
import logging
import json
import os
import errno
import atexit
import socket

script_dir = os.path.dirname(os.path.abspath(argv[0]))

logging.basicConfig(filename=os.path.dirname(os.path.abspath(argv[0]))+'/Si4713_RDS_Updater.log',level=logging.DEBUG)
logging.debug("----------")
logging.debug("Arguments %s", argv[1:])

fifo_path = script_dir + "/Si4713_FM_RDS_FIFO"
updater_name = "Si4713_RDS_Updater.py"

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
		if len(line) > 0:
			logging.debug(line.rstrip())
			if line == "EXIT":
				exit()
		else:
			#print "Empty line"
			sleep(1)
