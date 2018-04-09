#!/usr/bin/python

from sys import argv
from time import sleep
import logging
import json
import os
import errno
import subprocess
import socket

if len(argv) <= 1:
	print 'Usage: '
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

logging.basicConfig(filename=script_dir + '/Si4713_FM_RDS_callback.log',level=logging.DEBUG,format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
logging.info('----------')
logging.debug('Arguments %s', argv[1:])
logging.debug('Environ %s', os.environ)

fifo_path = script_dir + '/Si4713_FM_RDS_FIFO'
updater_path = script_dir + '/Si4713_RDS_Updater.py'

configfile = os.getenv('CFGDIR', '/home/fpp/media/config') + '/plugin.Si4713_FM_RDS'
config = {}
with open(configfile, 'r') as f:
	for line in f:
		(key, val) = line.split(' = ')
		config[key] = val.replace('"', '').strip()
logging.debug('Config %s', config)

# Always start the Updater since it does the real work for almost all command
try:
	logging.debug("Checking for socket lock by " + updater_path)
	lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
	lock_socket.bind('\0Si4713_RDS_Updater')
	lock_socket.close()
	logging.debug("Lock not found")
	logging.info("Starting " + updater_path)
	devnull = open(os.devnull, 'w')
	subprocess.Popen(["python", updater_path], stdin=devnull, stdout=devnull, stderr=devnull, close_fds=True)
except socket.error:
	logging.debug("Lock found - " + updater_path + " is running")

# Always setup FIFO
make_fifo()

if argv[1] == "--list":
	logging.info("Processing --list")
	with open(fifo_path, 'w') as fifo:
		fifo.write("INIT" + '\n')
	print "media,playlist"
	logging.info("Processing --list done")

elif argv[1] == "--reset":
	# Not used by FPPD, but used by plugin_setup.php
	logging.info("Processing --reset")
	with open(fifo_path, 'w') as fifo:
		fifo.write("RESET" + '\n')
	logging.info("Processing --reset done")

elif argv[1] == "--exit":
	# Not used by FPPD, but useful for testing
	logging.info("Processing --exit")
	with open(fifo_path, 'w') as fifo:
		fifo.write("EXIT" + '\n')
	logging.info("Processing --exit done")

elif argv[2] == "media":
	# TODO: When not type:pause or event?
	#	If RDS on, kill existing RDS script, kick off new RDS script to run for item duration
	logging.info('Processing media')
		
	# TODO: Exception handling for json?
	j = json.loads(argv[4])

	media_type = j['type'] if 'type' in j else 'pause'
	media_title = j['title'] if 'title' in j else '(No Title)'
	media_artist = j['artist'] if 'artist' in j else ''
	# TODO: Enhancement - Send play time to updater to allow a more graceful ends to the RDS for a song

	logging.info('Type is ' + media_type)
	logging.info('Title is ' + media_title)
	logging.info('Artist is ' + media_artist)

	with open(fifo_path, 'w') as fifo:
		if media_type == 'pause': # Other things to send blanks for?
			fifo.write('T\n'); # Empty Title
			fifo.write('A\n'); # Empty Artist
		else:
			fifo.write('T' + media_title + '\n');
			fifo.write('A' + media_artist + '\n');
	logging.info('Processing media done')		

elif argv[2] == 'playlist':
	# TODO: On Action:stop Kill existing RDS scripts if configured
	logging.info('Processing playlist')
		
	j = json.loads(argv[4])
	logging.debug(j['Action'])

	playlist_action = j['Action'] if 'Action' in j else 'stop'

	with open(fifo_path, 'w') as fifo:
		if playlist_action == 'start':
			fifo.write('START' + '\n')
		else:
			fifo.write('T\n'); # Empty Title
			fifo.write('A\n'); # Empty Artist
			# TODO: Send STOP is playlist is done?
	logging.info('Processing playlist done')
