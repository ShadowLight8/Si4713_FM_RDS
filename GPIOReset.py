#!/usr/bin/python2

from time import sleep
import RPi.GPIO as GPIO

GPIOResetPin = 4

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIOResetPin, GPIO.OUT)

# toggle pin
GPIO.output(GPIOResetPin, GPIO.HIGH)
sleep(0.1)
GPIO.output(GPIOResetPin, GPIO.LOW)
sleep(0.1)
GPIO.output(GPIOResetPin, GPIO.HIGH)
sleep(0.2)

GPIO.cleanup(GPIOResetPin)
