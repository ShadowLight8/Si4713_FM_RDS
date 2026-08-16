#!/bin/bash
set -e

echo Installing python3-smbus...
apt-get install -y python3-smbus

echo Flagging FPP for restart...
. ${FPPDIR:-/opt/fpp}/scripts/common
setSetting restartFlag 1
echo ...Done
