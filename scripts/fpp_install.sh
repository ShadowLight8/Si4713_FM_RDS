#!/bin/bash

echo Installing python3-smbus...
sudo apt-get install -y python3-smbus

echo Restarting FPP...
curl http://localhost/api/system/fppd/restart
echo ...Done
