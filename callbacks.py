#!/usr/bin/python2.7

from sys import argv
from time import sleep
import logging
import json
import os
import errno
import subprocess
import socket

script_dir = os.path.dirname(os.path.abspath(argv[0]))

logging.basicConfig(filename=script_dir+'/Si4713_FM_RDS.log',level=logging.DEBUG)
logging.debug("----------")
logging.debug("Arguments %s", argv[1:])

fifo_path = script_dir + "/Si4713_FM_RDS_FIFO"
updater_name = "Si4713_RDS_Updater.py"

# Config from os.path.abspath(argv[0])
# ../../config/plugin.Si4713_FM_RDS
# TODO: Not sure this is the right way to locate the config file, but it works

# TODO: If RDS is not enabled, exit?

if len(argv) > 1:
	if argv[1] == "--list":
		#sleep(5)
		logging.debug("Processing --list");
		try:
			logging.debug("Checking for socket lock")
			lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
			lock_socket.bind('\0Si4713_RDS_Updater')
			lock_socket.close()
			logging.debug("Lock not found")
			logging.debug("Starting " + script_dir + "/" + updater_name)

			devnull = open(os.devnull, 'w')
			subprocess.Popen(["python",script_dir + "/" + updater_name], stdin=devnull, stdout=devnull, stderr=devnull)
		except socket.error:
			logging.debug("Lock found - " + script_dir + "/" + updater_name + " is running")

		try:
			logging.debug("Setting up write side of fifo " + fifo_path)
			os.mkfifo(fifo_path)
		except OSError as oe:
			logging.debug("Already exists")
			if oe.errno != errno.EEXIST:
				raise

		with open(fifo_path, 'w') as fifo:
			fifo.write("INIT")
			fifo.flush()

		print "media,playlist"
		#sleep(5)
		exit()
	elif argv[1] == "--exit":
		try:
			logging.debug("Setting up write side of fifo " + fifo_path)
			os.mkfifo(fifo_path)
		except OSError as oe:
			logging.debug("Already exists")
			if oe.errno != errno.EEXIST:
				raise

		with open(fifo_path, 'w') as fifo:
			fifo.write("EXIT")
			fifo.flush()

	elif argv[2] == "media":
		# TODO: When not type:pause or event?
		#	If RDS on, kill existing RDS script, kick off new RDS script to run for item duration
		logging.debug("Media!")
	elif argv[2] == "playlist":
		# TODO: On Action:start
		#	Check I2C address, if bad, reset
		# TODO: On Action:stop
		#	Kill existing RDS scripts
		logging.debug("Playlist!")
else:
	print "Usage: ..."
