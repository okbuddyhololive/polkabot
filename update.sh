#!/usr/bin/bash

# update the system
sudo -S apt-get update && sudo apt-get upgrade -y

# move into the polkabot directory
cd ~/project-pretender

# update python packages
python3 -m pip install -r requirements.txt --upgrade

# pull the latest code
git pull origin main

# restart the service
sudo systemctl restart polkabot.service