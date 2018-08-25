#!/usr/bin/python

# v.1.1
# Code reused from Adafruit's example code and Hansipete's original code
# Converted into a reusable class by djazz (https://github.com/daniel-j/Adafruit-Si4713-RPi)
# Uses Adafruit_I2C and RPi.GPIO, make sure those are available!
# See the example at the end of this file for help!

# Additional v1.1 changes by ShadowLight8 / Nick Anderson
#  Removed example code at end of file
#  Timing changes to get more consistent behavior from the Si4713
#  Added Preemphasis variable to allow control from outside of the class
#  Fixed a bug in setRDSBuffer
#  Changed logic when Si4713 is missing, mostly to return false from begin

from time import sleep
import RPi.GPIO as GPIO
from Adafruit_I2C import Adafruit_I2C

class Adafruit_Si4713(Adafruit_I2C):

	SI4710_ADDR0 = 0x11  # if SEN is low
	SI4710_ADDR1 = 0x63  # if SEN is high, default!
	SI4710_STATUS_CTS = 0x80

	## Commands ##
	SI4710_CMD_POWER_UP        = 0x01
	SI4710_CMD_GET_REV         = 0x10
	SI4710_CMD_POWER_DOWN      = 0x11
	SI4710_CMD_SET_PROPERTY    = 0x12
	SI4710_CMD_GET_PROPERTY    = 0x13
	SI4710_CMD_GET_INT_STATUS  = 0x14
	SI4710_CMD_PATCH_ARGS      = 0x15
	SI4710_CMD_PATCH_DATA      = 0x16
	SI4710_CMD_TX_TUNE_FREQ    = 0x30
	SI4710_CMD_TX_TUNE_POWER   = 0x31
	SI4710_CMD_TX_TUNE_MEASURE = 0x32
	SI4710_CMD_TX_TUNE_STATUS  = 0x33
	SI4710_CMD_TX_ASQ_STATUS   = 0x34
	SI4710_CMD_TX_RDS_BUFF     = 0x35
	SI4710_CMD_TX_RDS_PS       = 0x36
	SI4710_CMD_TX_AGC_OVERRIDE = 0x48
	SI4710_CMD_GPO_CTL         = 0x80
	SI4710_CMD_GPO_SET         = 0x81

	## Parameters ##
	SI4713_PROP_GPO_IEN = 0x0001
	SI4713_PROP_DIGITAL_INPUT_FORMAT = 0x0101
	SI4713_PROP_DIGITAL_INPUT_SAMPLE_RATE = 0x0103
	SI4713_PROP_REFCLK_FREQ = 0x0201
	SI4713_PROP_REFCLK_PRESCALE = 0x0202
	SI4713_PROP_TX_COMPONENT_ENABLE = 0x2100
	SI4713_PROP_TX_AUDIO_DEVIATION = 0x2101
	SI4713_PROP_TX_PILOT_DEVIATION = 0x2102
	SI4713_PROP_TX_RDS_DEVIATION = 0x2103
	SI4713_PROP_TX_LINE_LEVEL_INPUT_LEVEL = 0x2104
	SI4713_PROP_TX_LINE_INPUT_MUTE = 0x2105
	SI4713_PROP_TX_PREEMPHASIS = 0x2106
	SI4713_PROP_TX_PILOT_FREQUENCY = 0x2107
	SI4713_PROP_TX_ACOMP_ENABLE = 0x2200
	SI4713_PROP_TX_ACOMP_THRESHOLD = 0x2201
	SI4713_PROP_TX_ATTACK_TIME = 0x2202
	SI4713_PROP_TX_RELEASE_TIME = 0x2203
	SI4713_PROP_TX_ACOMP_GAIN = 0x2204
	SI4713_PROP_TX_LIMITER_RELEASE_TIME = 0x2205
	SI4713_PROP_TX_ASQ_INTERRUPT_SOURCE = 0x2300
	SI4713_PROP_TX_ASQ_LEVEL_LOW = 0x2301
	SI4713_PROP_TX_ASQ_DURATION_LOW = 0x2302
	SI4713_PROP_TX_ASQ_LEVEL_HIGH = 0x2303
	SI4713_PROP_TX_ASQ_DURATION_HIGH = 0x2304

	SI4713_PROP_TX_RDS_INTERRUPT_SOURCE = 0x2C00
	SI4713_PROP_TX_RDS_PI = 0x2C01
	SI4713_PROP_TX_RDS_PS_MIX = 0x2C02
	SI4713_PROP_TX_RDS_PS_MISC = 0x2C03
	SI4713_PROP_TX_RDS_PS_REPEAT_COUNT = 0x2C04
	SI4713_PROP_TX_RDS_MESSAGE_COUNT = 0x2C05
	SI4713_PROP_TX_RDS_PS_AF = 0x2C06
	SI4713_PROP_TX_RDS_FIFO_SIZE = 0x2C07

	def __init__(self, resetpin = 4, addr = None, busnum = -1, debug = False):
		self._rst = resetpin

		if addr is None:
			addr = self.SI4710_ADDR1

		self._addr = addr
		self._busnum = busnum
		self._debug = debug

		self.currFreq = 0
		self.currdBuV = 0
		self.currAntCap = 0
		self.currNoiseLevel = 0
		self.currASQ = 0
		self.currInLevel = 0

		# Additional properties
		self.preemphasis = 0

		# for restoring state
		self._freq = None
		self._power = None
		self._rdsStation = None
		self._rdsBuffer = None

	def begin(self):

		self.reset()

		self.bus = Adafruit_I2C(self._addr, self._busnum, self._debug)

		if not self.powerUp():
			print 'Power Up issue'
			return False

		if self.getRev() is not 13:
			print 'getRev issue'
			return False

		return True

	def restart(self):
		sleep(5)
		if self.begin():

			# restore values
			if self._power:
				self.setTXpower(self._power)

			if self._freq:
				self.tuneFM(self._freq)

			if self._rdsStation or self._rdsBuffer:
				self.beginRDS()
				if self._rdsStation:
					self.setRDSstation(self._rdsStation)
				if self._rdsBuffer:
					self.setRDSbuffer(self._rdsBuffer)

			self.readASQ()
			self.readTuneStatus()

		else:
			sleep(5)
			self.restart()


	def setProperty(self, prop, val):
		args = [0, prop >> 8, prop & 0xFF, val >> 8, val & 0xFF]
		
		res = self.bus.writeList(self.SI4710_CMD_SET_PROPERTY, args)

		sleep(0.05)
		return res

	def sendCommand(self, cmd, args):
		res = self.bus.writeList(cmd, args)

		sleep(0.05)
		#self.waitStatus()
		return res

	def getStatus(self):
		return self.bus.readU8(self.SI4710_CMD_GET_INT_STATUS)

	def waitStatus(self, waitForByte=0):
		timeout = 50 # about 2.5 seconds
		response = 0
		while True:
			response = self.getStatus()
			#print "response:", response
			if response is -1:
				self.restart()
				return
			if waitForByte == 0 and response != 0:
				break
			elif response == waitForByte:
				break
			sleep(0.05)
			timeout -= 1
			if timeout == 0:
				break

		if timeout > 0:
			return True
		else:
			print "waitForByte TIMEOUT"
			return False

	def reset(self):
		if self._rst > 0:
			GPIO.setwarnings(False)
			GPIO.setmode(GPIO.BCM)
			
			GPIO.setup(self._rst, GPIO.OUT)

			# CHECK: Longer reset time?
			# toggle pin
			GPIO.output(self._rst, GPIO.HIGH)
			sleep(0.1) # was 0.1
			GPIO.output(self._rst, GPIO.LOW)
			sleep(0.1) # was 0.1
			GPIO.output(self._rst, GPIO.HIGH)
			sleep(0.2) # give it some time to come back

			GPIO.cleanup(self._rst)

	def powerUp(self):
		#CHECK: Longer delay after power up of 500ms prior to first tune
		if self.sendCommand(self.SI4710_CMD_POWER_UP, [0x12, 0x50]) is -1:
			return False
		#sleep(0.5);

		self.setProperty(self.SI4713_PROP_REFCLK_FREQ, 32768) # crystal is 32.768
		self.setProperty(self.SI4713_PROP_TX_PREEMPHASIS, self.preemphasis) # 75uS pre-emph (default for US)
		self.setProperty(self.SI4713_PROP_TX_ACOMP_ENABLE, 0x03) # turn on limiter and AGC
		#self.setProperty(self.SI4713_PROP_TX_ACOMP_GAIN, 10) # max gain?

		# aggressive compression
		self.setProperty(self.SI4713_PROP_TX_ACOMP_THRESHOLD, 0x10000-15) # -15 dBFS
		self.setProperty(self.SI4713_PROP_TX_ATTACK_TIME, 0) # 0.5 ms
		self.setProperty(self.SI4713_PROP_TX_RELEASE_TIME, 4) # 1000 ms
		self.setProperty(self.SI4713_PROP_TX_ACOMP_GAIN, 5) # dB

		return True

	def getRev(self):
		if self.sendCommand(self.SI4710_CMD_GET_REV, [0x00]) is -1:
			#If sendCommand fails, stop
			#self.restart()
			return False

		response = self.bus.readList(0x00, 9)
		if response is -1:
			self.restart()
			return

		pn = response[1]
		fw = response[2] << 8 | response[3]
		patch = response[4] << 8 | response[5]
		cmp = response[6] << 8 | response[7]
		chiprev = response[8]

		#print "pn - ", pn, "fw - ", fw, "patch - ", patch, "cmp - ", cmp, "chiprev - ", chiprev

		return pn


	def tuneFM(self, freq):
		self._freq = freq
		res = self.sendCommand(self.SI4710_CMD_TX_TUNE_FREQ, [0, freq >> 8, freq & 0xff])
		sleep(0.11)
		if res is -1:
			self.restart()
		else:
			self.waitStatus(0x81)

	def setTXpower(self, power, antcap = 0):
		self._power = power
		res = self.sendCommand(self.SI4710_CMD_TX_TUNE_POWER, [0, 0, power, antcap])
		sleep(0.1)
		if res is -1:
			self.restart()
		else:
			self.waitStatus(0x81)

	def readASQ(self):
		res = self.sendCommand(self.SI4710_CMD_TX_ASQ_STATUS, [0x1])
		if res is -1:
			self.restart()
			return

		response = self.bus.readList(0x00, 5)
		if response is -1:
			self.restart()
			return

		self.currASQ = response[1]
		self.currInLevel = response[4]

		if self.currInLevel > 127:
			self.currInLevel -= 256

		#print "ASQ:", hex(self.currASQ), "- InLevel:", self.currInLevel, "dBfs"

	def readTuneStatus(self):
		res = self.sendCommand(self.SI4710_CMD_TX_TUNE_STATUS, [0x1])
		if res == -1:
			self.restart()
			return

		response = self.bus.readList(0x00, 8)
		if response == -1:
			self.restart()
			return

		self.currFreq = response[2] << 8 | response[3]
		self.currdBuV = response[5]
		self.currAntCap = response[6] # antenna capacitance (0-191)
		self.currNoiseLevel = response[7]

		#print "Freq:", self.currFreq, " MHz - Power:", self.currdBuV, "dBuV - ANTcap:", self.currAntCap, " - Noise level:", self.currNoiseLevel

	def readTuneMeasure(self, freq):
		# check freq is multiple of 50khz
		if freq % 5 != 0:
			freq -= (freq % 5)

		res = self.sendCommand(self.SI4710_CMD_TX_TUNE_MEASURE, [0, freq >> 8, freq & 0xff, 0])
		if res == -1:
			self.restart()
		else:
			self.waitStatus(0x81)

	def beginRDS(self):
		# 66.25KHz (default is 68.25)
		self.setProperty(self.SI4713_PROP_TX_AUDIO_DEVIATION, 6625)
		# 2KHz (default)
		self.setProperty(self.SI4713_PROP_TX_RDS_DEVIATION, 200)

		# RDS IRQ
		self.setProperty(self.SI4713_PROP_TX_RDS_INTERRUPT_SOURCE, 0x0001)
		# program identifier
		self.setProperty(self.SI4713_PROP_TX_RDS_PI, 0x40A7)
		# 50% mix (default)
		self.setProperty(self.SI4713_PROP_TX_RDS_PS_MIX, 0x03)
		# RDSD0 & RDSMS (default)
		self.setProperty(self.SI4713_PROP_TX_RDS_PS_MISC, 0x1848)
		# 3 repeats (default)
		self.setProperty(self.SI4713_PROP_TX_RDS_PS_REPEAT_COUNT, 3)

		self.setProperty(self.SI4713_PROP_TX_RDS_MESSAGE_COUNT, 1)
		self.setProperty(self.SI4713_PROP_TX_RDS_PS_AF, 0xE0E0) # no AF
		self.setProperty(self.SI4713_PROP_TX_RDS_FIFO_SIZE, 0)

		self.setProperty(self.SI4713_PROP_TX_COMPONENT_ENABLE, 0x0007)

	def setRDSstation(self, s):
		self._rdsStation = s
		# empty station name to start from
		stationName = [' ',' ',' ',' ', ' ',' ',' ',' ', ' ',' ',' ',' ', ' ',' ',' ',' ']

		# calc number of slots needed
		slots = (len(s)+3) / 4

		i = 0
		for char in s:
			stationName[i] = char
			i += 1

		# cycle through slots
		for i in range(4):
			res = self.sendCommand(self.SI4710_CMD_TX_RDS_PS, [i, ord(stationName[i*4]), ord(stationName[(i*4)+1]), ord(stationName[(i*4)+2]), ord(stationName[(i*4)+3]), 0])
			if res == -1:
				self.restart()
				return

	def setRDSbuffer(self, s):
		self._rdsBuffer = s
		bufferArray = [' ',' ',' ',' ', ' ',' ',' ',' ', ' ',' ',' ',' ', ' ',' ',' ',' ', ' ',' ',' ',' ', ' ',' ',' ',' ', ' ',' ',' ',' ', ' ',' ',' ',' ']

		# calc number of slots needed
		slots = (len(s)+3) / 4

		i = 0
		for char in s:
			bufferArray[i] = char
			i += 1

		# cycle through slots
		for i in range(slots):
			if i == 0:
				secondByte = 0x06
			else:
				secondByte = 0x04
			
			res = self.sendCommand(self.SI4710_CMD_TX_RDS_BUFF, [secondByte, 0x20, i, ord(bufferArray[i*4]), ord(bufferArray[(i*4)+1]), ord(bufferArray[(i*4)+2]), ord(bufferArray[(i*4)+3]), 0])
			if res == -1:
				self.restart()
				return

	def setGPIOctrl(self, x):
		self.sendCommand(self.SI4710_CMD_GPO_CTL, [x])

	def setGPIO(self, x):
		self.sendCommand(self.SI4710_CMD_GPO_SET, [x])
