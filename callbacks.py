#!/usr/bin/python

import logging
import json
import os
import errno
import subprocess
import socket
from sys import argv
from time import sleep

if len(argv) <= 1:
	print 'Usage:'
	print '   --list     | Used by fppd at startup. Used to start up the Si4713_RDS_Updater.py script'
	print '   --reset    | Function by plugin_setup.php to reset the GPIO pin connected to the Si4713'
	print '   --exit     | Function used to shutdown the Si4713_RDS_Updater.py script'
	print '   --type media --data \'{...}\'    | Used by fppd when a new items starts in a playlist'
	print '   --type playlist --data \'{...}\' | Used by fppd when a playlist starts or stops'
	exit()

def make_fifo():
	try:
		logging.debug('Setting up write side of fifo %s', fifo_path)
		os.mkfifo(fifo_path)
	except OSError as oe:
		if oe.errno != errno.EEXIST:
			raise
		else:
			logging.debug('Fifo already exists')

script_dir = os.path.dirname(os.path.abspath(argv[0]))

logging.basicConfig(filename=script_dir + '/Si4713_Callbacks.log', level=logging.INFO, format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
logging.info('----------')
logging.debug('Arguments %s', argv[1:])
logging.debug('Environ %s', os.environ)

fifo_path = script_dir + '/Si4713_FM_RDS_FIFO'

# Always start the Updater since it does the real work for almost all command
updater_path = script_dir + '/Si4713_RDS_Updater.py'
try:
	logging.debug("Checking for socket lock by %s", updater_path)
	lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
	lock_socket.bind('\0Si4713_RDS_Updater')
	lock_socket.close()
	logging.debug("Lock not found")
	logging.info("Starting %s", updater_path)
	devnull = open(os.devnull, 'w')
	subprocess.Popen(["python", updater_path], stdin=devnull, stdout=devnull, stderr=devnull, close_fds=True)
except socket.error:
	logging.debug("Lock found - %s is running", updater_path)

# Always setup FIFO
make_fifo()

if argv[1] == "--list":
	logging.info("Processing --list")
	with open(fifo_path, 'w') as fifo:
		fifo.write("INIT" + '\n')
	print "media,playlist"
	logging.debug("Processing --list done")

elif argv[1] == "--reset":
	# Not used by FPPD, but used by plugin_setup.php
	logging.info("Processing --reset")
	with open(fifo_path, 'w') as fifo:
		fifo.write("RESET" + '\n')
	logging.debug("Processing --reset done")

elif argv[1] == "--exit":
	# Not used by FPPD, but useful for testing
	logging.info("Processing --exit")
	with open(fifo_path, 'w') as fifo:
		fifo.write("EXIT" + '\n')
	logging.debug("Processing --exit done")

elif argv[2] == "media":
	# TODO: When not type:pause or event?
	logging.info('Processing media')
		
	# TODO: Exception handling for json?
	j = json.loads(argv[4])

	media_type = j['type'] if 'type' in j else 'pause'
	media_title = j['title'] if 'title' in j else 'No Title'
	media_artist = j['artist'] if 'artist' in j else ''
	# TODO: Enhancement - Send play time to updater to allow a more graceful ends to the RDS for a song

	# TODO: Info to much logging?
	logging.info('Type is %s', media_type)
	logging.info('Title is %s', media_title)
	logging.info('Artist is %s', media_artist)

	with open(fifo_path, 'w') as fifo:
		if media_type == 'pause': # TODO: Other things to send blanks for?
			fifo.write('T\n'); # Blank Title
			fifo.write('A\n'); # Blank Artist
		else:
			fifo.write('T' + media_title + '\n');
			fifo.write('A' + media_artist + '\n');
	logging.debug('Processing media done')		

elif argv[2] == 'playlist':
	logging.info('Processing playlist')
		
	# TODO: Exception handling for json?
	j = json.loads(argv[4])

	playlist_action = j['Action'] if 'Action' in j else 'stop'

	logging.info('Playlist action %s', j['Action'])

	with open(fifo_path, 'w') as fifo:
		if playlist_action == 'start':
			fifo.write('START' + '\n')
		else:
			fifo.write('T\n'); # Blank Title
			fifo.write('A\n'); # Blank Artist
	logging.debug('Processing playlist done')

