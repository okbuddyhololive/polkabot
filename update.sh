#!/usr/bin/bash

# update the system
sudo apt-get update && sudo apt-get upgrade -y

# update python packages
python3 -m pip install -r requirements.txt --upgrade

# pull the latest code
git pull origin main

# restart the service
sudo systemctl restart polkabot.service