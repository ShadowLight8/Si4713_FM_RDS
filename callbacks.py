#!/usr/bin/python

import logging
import json
import os
import errno
import subprocess
import socket
import sys
from sys import argv
from time import sleep

if len(argv) <= 1:
	print('Usage:')
	print('   --list     | Used by fppd at startup. Used to start up the Si4713_RDS_Updater.py script')
	print('   --reset    | Function by plugin_setup.php to reset the GPIO pin connected to the Si4713')
	print('   --exit     | Function used to shutdown the Si4713_RDS_Updater.py script')
	print('   --type media --data \'{...}\'    | Used by fppd when a new items starts in a playlist')
	print( '   --type playlist --data \'{...}\' | Used by fppd when a playlist starts or stops')
	print('Note: Running with sudo might be needed for manual execution')
	exit()

script_dir = os.path.dirname(os.path.abspath(argv[0]))

logging.basicConfig(filename=script_dir + '/Si4713_callbacks.log', level=logging.INFO, format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
logging.info('----------')
logging.debug('Arguments %s', argv[1:])

try:
	import smbus
except ImportError as impErr:
	logging.error("Failed to import {}.".format(impErr.args[0]))
	sys.exit(1)

# Environ has a few useful items when FPPD runs callbacks.py, but logging it all the time, even at debug, is too much
#logging.debug('Environ %s', os.environ)

# Always start the Updater since it does the real work for all command
updater_path = script_dir + '/Si4713_RDS_Updater.py'
try:
	logging.debug('Checking for socket lock by %s', updater_path)
	lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
	lock_socket.bind('\0Si4713_RDS_Updater')
	lock_socket.close()
	logging.debug('Lock not found')
	logging.info('Starting %s', updater_path)
	devnull = open(os.devnull, 'w')
	subprocess.Popen(['python', updater_path], stdin=devnull, stdout=devnull, stderr=devnull, close_fds=True)
except socket.error:
	logging.debug('Lock found - %s is running', updater_path)

# Always setup FIFO
fifo_path = script_dir + '/Si4713_FM_RDS_FIFO'
try:
	logging.debug('Setting up write side of fifo %s', fifo_path)
	os.mkfifo(fifo_path)
except OSError as oe:
	if oe.errno != errno.EEXIST:
		raise
	else:
		logging.debug('Fifo already exists')

with open(fifo_path, 'w') as fifo:
	logging.info('Processing %s', argv[1])
	if argv[1] == '--list':
		fifo.write('INIT\n')
		print('media,playlist')

	elif argv[1] == '--reset':
		# Not used by FPPD, but used by plugin_setup.php
		fifo.write('RESET\n')

	elif argv[1] == '--exit':
		# Not used by FPPD, but useful for testing
		fifo.write('EXIT\n')

	elif argv[1] == '--type' and argv[2] == 'media':
		logging.info('Type media')
		
		# TODO: Exception handling for json?
		j = json.loads(argv[4])

		# When default values are sent over fifo, other side more or less ignores them
		media_type = j['type'] if 'type' in j else 'pause'
		media_title = j['title'] if 'title' in j else ''
		media_artist = j['artist'] if 'artist' in j else ''
		media_tracknum = str(j['track']) if 'track' in j else '0'
		media_length = str(j['length']) if 'length' in j else '0'

		logging.debug('Type is %s', media_type)
		logging.debug('Title is %s', media_title)
		logging.debug('Artist is %s', media_artist)
		logging.debug('Track # is %s', media_tracknum)
		logging.debug('Length is %s', media_length)

		if media_type == 'pause' or media_type == 'event':
			fifo.write('T\n') # Blank Title
			fifo.write('A\n') # Blank Artist
		else:
			fifo.write('T' + media_title + '\n')
			fifo.write('A' + media_artist + '\n')
		# TODO: Will tracknum and length never show up at the wrong time?
		fifo.write('N' + media_tracknum + '\n')
		fifo.write('L' + media_length + '\n')

	elif argv[1] == '--type' and argv[2] == 'playlist':
		logging.info('Type playlist')

		# TODO: Exception handling for json?
		j = json.loads(argv[4])

		playlist_action = j['Action'] if 'Action' in j else 'stop'

		logging.info('Playlist action %s', j['Action'])

		if playlist_action == 'start': # or playlist_action == 'playing':
			fifo.write('START\n')
		elif playlist_action == 'stop':
			fifo.write('STOP\n')
	logging.debug('Processing done')
