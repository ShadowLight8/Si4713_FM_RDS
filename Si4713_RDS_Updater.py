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

class RadioBuffer(object):
# fragsize: How long the block from data will be. Likely 8 or 32
# delay: Time, in seconds, between frag updates
# data: Complete string of all data to be sent
# fragments: How many block of 8 or 32 characters the data is
# frag: Current fragment to be sent by radio
# tick: Counter to track time until next delay interval reached

	def __init__(self, data='', fragsize=8, delay=4):
		self.fragsize = fragsize
		self.delay = delay
		self.updateData(data)

	def updateData(self, data):
		self.data = data.ljust(self.fragsize) # Ensure at least one fragment
		self.__fragments = (len(self.data) - 1) // self.fragsize + 1
		self.__tick = self.delay - 1 # Setup nextTick to return true
		self.__frag = self.__fragments - 1 # Setup currentFragment to start at the beginning

	def currentFragment(self):
		return (self.data[self.fragsize * self.__frag:self.fragsize * (self.__frag + 1)]).ljust(self.fragsize)

	def nextTick(self):
		self.__tick = (self.__tick + 1) % self.delay
		if self.__tick == 0:
			self.__frag = (self.__frag + 1) % self.__fragments
			return True
		return False

@atexit.register
def cleanup():
	try:
		logging.debug('Cleaning up fifo')
		os.unlink(fifo_path)
	except:
		pass

def read_config():
	global config
	config = {
		'Start': 'FPPDStart',
		'Stop': 'Never',
		'GPIONumReset': '4',
		'Frequency': '100.10',
		'Power': '113',
		'Preemphasis': '75us',
		'AntCap': '32',
		'EnableRDS': 'True',
		'StationDelay': '4',
		'StationText': 'Happy   Hallo-     -ween',
		'StationTitle': 'True',
		'StationArtist': 'True',
		'StationTrackNumPre': '',
		'StationTrackNum': 'True',
		'StationTrackNumSuf': 'of 4',
		'RDSTextDelay': '7',
		'RDSTextText': 'Happy   Hallo-     -ween',
		'RDSTextTitle': 'True',
		'RDSTextArtist': 'True',
		'RDSTextTrackNumPre': 'Track ',
		'RDSTextTrackNum': 'True',
		'RDSTextTrackNumSuf': 'of 4',
		'Pty': '2',
		'LoggingLevel': 'INFO'
	}

	configfile = os.getenv('CFGDIR', '/home/fpp/media/config') + '/plugin.Si4713_FM_RDS'
	try:
		with open(configfile, 'r') as f:
        		for line in f:
                		(key, val) = line.split(' = ')
	                	config[key] = val.replace('"', '').strip()
	except IOError:
		logging.warn('No config file found, using defaults.')
	logging.getLogger().setLevel(config['LoggingLevel'])
	logging.debug('Config %s', config)

def init_actions():
	read_config()
	RDSStation.delay = int(config['StationDelay'])
	RDSStation.updateData(config['StationText'])
	RDSText.delay = int(config['RDSTextDelay'])
	RDSText.updateData(config['RDSTextText'])

def Si4713_start():
	global radio
	global radio_ready
	logging.info('Si4713 Start')
	radio = Adafruit_Si4713(resetpin = int(config['GPIONumReset']))

	if config['Preemphasis'] == '50us':
		radio.preemphasis = 1

	if not radio.begin():
		logging.error('Unable to initialize radio. Check that the Si4713 is connected, then restart FPPD.')
		exit(1)

	radio.setTXpower(int(config['Power']), int(config['AntCap']))
	radio.tuneFM(int(float(config['Frequency'])*100))
	radio.pty = int(config['Pty'])

	if config['EnableRDS'] == 'True':
		radio.beginRDS()
		radio.setRDSstation(RDSStation.currentFragment())

	radio_ready = True
	logging.info('Radio initialized')
	Si4713_status()
	
def Si4713_status():
	logging.debug('Radio status')
	radio.readTuneStatus()
	radio.readASQ()
	logging.info('Radio status --- Power: %s dBuV - ANTcap: %s - Noise level: %s - Frequency: %s - ASQ: %s - Inlevel: %s dBfs', radio.currdBuV, radio.currAntCap, radio.currNoiseLevel, radio.currFreq, hex(radio.currASQ), radio.currInLevel)
	if radio.currFreq != int(float(config['Frequency'])*100):
		logging.error('Radio frequency of %s does not match %s which is configured from %s', radio.currFreq, config['Frequency'], int(float(config['Frequency'])*100))
	if radio.currdBuV != int(config['Power']):
		logging.error('Radio power of %s does not match %s which is configured', radio.currdBuV, config['Power'])
	
def updateRDSData():
	logging.info('Updating RDS Data')
	logging.debug('Title %s', title)
	logging.debug('Artist %s', artist)
	logging.debug('Tracknum %s', tracknum)
	
	tmp_StationTitle = title if config['StationTitle'] == 'True' else ''
	tmp_StationArtist = artist if config['StationArtist'] == 'True' else ''
	tmp_StationTrackNum = ''
	if config['StationTrackNum'] == 'True' and tracknum != '0' and tracknum !='':
		tmp_StationTrackNum = '{} {} {}'.format(config['StationTrackNumPre'], tracknum, config['StationTrackNumSuf']).strip()

	tmp_RDSTextTitle = title if config['RDSTextTitle'] == 'True' else ''
	tmp_RDSTextArtist = artist if config['RDSTextArtist'] == 'True' else ''
	tmp_RDSTextTrackNum = ''
	if config['RDSTextTrackNum'] == 'True' and tracknum != '0' and tracknum !='':
		tmp_RDSTextTrackNum = '{} {} {}'.format(config['RDSTextTrackNumPre'], tracknum, config['RDSTextTrackNumSuf']).strip()

	Stationstr = '{s: <{sw}}{t: <{tw}}{a: <{aw}}{n: <{nw}}'.format( \
		s=config['StationText'], sw=nearest(config['StationText'], 8), \
		t=tmp_StationTitle, tw=nearest(tmp_StationTitle, 8), \
		a=tmp_StationArtist, aw=nearest(tmp_StationArtist, 8), \
		n=tmp_StationTrackNum, nw=nearest(tmp_StationTrackNum, 8))

	RDSTextstr = '{s: <{sw}}{t: <{tw}}{a: <{aw}}{n: <{nw}}'.format( \
		s=config['RDSTextText'], sw=nearest(config['RDSTextText'], 32), \
		t=tmp_RDSTextTitle, tw=nearest(tmp_RDSTextTitle,32), \
		a=tmp_RDSTextArtist, aw=nearest(tmp_RDSTextArtist,32), \
		n=tmp_RDSTextTrackNum, nw=nearest(tmp_RDSTextTrackNum, 32))

	logging.info('Updated Station Text [%s]', Stationstr)
	logging.info('Updated RDS Text [%s]', RDSTextstr)

	RDSStation.updateData(Stationstr)
	RDSText.updateData(RDSTextstr)

def nearest(str, size):
	# -(-X // Y) functions as ceiling division
	return -(-len(str) // size) * size

# Common variables
radio_ready = False

RDSStation = RadioBuffer('', 8, 4)
RDSText = RadioBuffer('', 32, 7)

title = ''
artist = ''
tracknum = ''
length = 0

radio = None
config = {}

# Setup logging
script_dir = os.path.dirname(os.path.abspath(argv[0]))

logging.basicConfig(filename=script_dir + '/Si4713_updater.log', level=logging.DEBUG, format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
logging.info("----------")

init_actions()

# Establish lock via socket or exit if failed
try:
	lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
	lock_socket.bind('\0Si4713_RDS_Updater')
	logging.debug('Lock created')
except:
	logging.error('Unable to create lock. Another instance of Si4713_RDS_Updater.py running?')
	exit(1)

# Setup fifo
fifo_path = script_dir + "/Si4713_FM_RDS_FIFO"
try:
	logging.debug('Setting up read side of fifo %s', fifo_path)
	os.mkfifo(fifo_path)
except OSError as oe:
	if oe.errno != errno.EEXIST:
		raise
	else:
		logging.debug('Fifo already exists')

# Main loop
with open(fifo_path, 'r', 0) as fifo:
	while True:
		line = fifo.readline().rstrip()
		if len(line) > 0:
			logging.debug('line %s', line)
			if line == 'EXIT':
				logging.info('Processing exit')
				radio.reset()
				exit()

			elif line == 'RESET':
				logging.info('Processing reset')
				read_config()
				radio = None
				radio = Adafruit_Si4713(resetpin = int(config['GPIONumReset']))
				radio.reset()
				radio_ready = False
				if config['Start'] == "FPPDStart":
					Si4713_start()

			elif line == 'INIT':
				logging.info('Processing init')
				init_actions()
				if config['Start'] == "FPPDStart":
					Si4713_start()

			elif line == 'START':
				logging.info('Processing start')
				if config['Start'] == "PlaylistStart":
					Si4713_start()

			elif line == 'STOP':
				logging.info('Processing stop')
				title = ''
				artist = ''
				tracknum = ''
				updateRDSData()

				if config['Stop'] == "PlaylistStop":
					radio.reset()
					radio = None
					radio_ready = False
					logging.info('Radio stopped')

			elif line[0] == 'T':
				logging.debug('Processing title')
				title = line[1:]

			elif line[0] == 'A':
				logging.debug('Processing artist')
				artist = line[1:]

			elif line[0] == 'N':
				logging.debug('Processing track number')
				tracknum = line[1:]
				# TANL is always sent together with N being last item for RDS, so we only need to update the RDS Data once with the new values
				updateRDSData()
				# Check radio status between each track
				Si4713_status()

			elif line[0] == 'L':
				logging.debug('Processing length')
				length = max(int(line[1:10]) - max(int(config['StationDelay']), int(config['RDSTextDelay'])), 1)
				logging.debug('Length %s', int(length))

			else:
				logging.error('Unknown fifo input %s', line)

		else:
			if radio_ready:
				if RDSStation.nextTick():
					logging.debug('Station Fragment [%s]', RDSStation.currentFragment())
					radio.setRDSstation(RDSStation.currentFragment())
				if RDSText.nextTick():
					logging.debug('Buffer Fragment  [%s]', RDSText.currentFragment())
					radio.setRDSbuffer(RDSText.currentFragment())

			length = length - 1
			if length == 0:
				title = ''
				artist = ''
				tracknum = ''
				updateRDSData()

			# Sleep until the top of the next second
			sleep ((1000000 - datetime.now().microsecond) / 1000000.0)
