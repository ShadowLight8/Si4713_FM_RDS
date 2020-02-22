# Si4713_FM_RDS
Si4713_FM_RDS Plugin for Falcon Player (FPP)

Using a Raspberry Pi and Adafruit's Si4713 FM transmitter breakout board with RDS or Radio Text support. This plugin allows the Falcon Player (FPP) to control the Si4713 FM transmitter, including sending RDS or Radio Text messages out on the broadcast.

FPP reads the Title, Artist, and Track Number from the media's metadata, which is sent out as RDS data.

## Instructions
### Installation
In FPP, under Content Setup, open the Plugin Manager. Find "Si4713 FM and RDS" and install. A restart of FPPD is needed.
Can be manually added by using https://raw.githubusercontent.com/ShadowLight8/Si4713_FM_RDS/master/pluginInfo.json

### Initial setup - Hardware
- Physical connection from Pi -> Si4713
  - Pin 3 (SDA1) -> SDA
  - Pin 4 (+5v) -> Vin
  - Pin 5 (SCL1) -> SCL
  - Pin 6 (GND) -> GND
  - Pin 7 (GPIO4) -> RST
- USB sound card and a short audio cable to go from the Pi to the Si4713

### FPP Plugin Info
Most recently tested on v3.6.1-7-gd1d56049 as of 2/22/2020
Updated for the FPP v3.x plugin standards
Originally built to follow the FPP v2.x plugin standards - https://github.com/FalconChristmas/fpp/commit/4d8dd95
Additional discussion on forum thread - https://falconchristmas.com/forum/index.php/topic,10496.45.html

## Credits, Thanks, and Links
### Adafruit's Si4713 Breakout Board
https://www.adafruit.com/product/1958

### Python class for Si4713
Converted into a reusable class by djazz/daniel-j - https://github.com/daniel-j/Adafruit-Si4713-RPi
Code reused from Adafruit's example code and Hansipete's original code. Original code is from this Adafruit forums thread - https://forums.adafruit.com/viewtopic.php?f=50&t=58453

### Adafruit's I2C library
https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/blob/legacy/Adafruit_I2C/Adafruit_I2C.py

### FPP Plugin examples and inspiration:
Thanks to drlucase for fpp-edmrds - https://github.com/drlucas/fpp-edmrds

Thanks for Materdaddy for fpp-vastfmt - https://github.com/Materdaddy/fpp-vastfmt
