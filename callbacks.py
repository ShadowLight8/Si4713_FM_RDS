#!/usr/bin/env python

from sys import argv
import logging
import json
import os

logging.basicConfig(filename=os.path.dirname(os.path.abspath(argv[0]))+'/Si4713_FM_RDS.log',level=logging.DEBUG)
logging.debug("----------")
logging.debug("Arguments %s", argv[1:])

# Config from os.path.abspath(argv[0])
# ../../config/plugin.Si4713_FM_RDS
# TODO: Not sure this is the right way to locate the config file, but it works

if len(argv) > 1:
	if argv[1] == "--list":
		# TODO: If configured, reset and startup Si4713 prior to returning
		print "media,playlist"
		exit()
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
