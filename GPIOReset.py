#!/usr/bin/env python

from time import sleep
import RPi.GPIO as GPIO
from sys import argv

print("Resetting GPIO {}".format(argv[1]))

GPIOReset = int(argv[1])

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIOReset, GPIO.OUT)

# toggle pin
GPIO.output(GPIOReset, GPIO.HIGH)
sleep(0.1)
GPIO.output(GPIOReset, GPIO.LOW)
sleep(0.1)
GPIO.output(GPIOReset, GPIO.HIGH)
sleep(0.2)

GPIO.cleanup(GPIOReset)

print("Done")
