#!/bin/bash

# update the system
sudo -S apt-get update && sudo apt-get upgrade -y

# move into the polkabot directory
cd ~/polkabot

# activate the virtual environment and update Python packages
source .venv/bin/activate && python3 -m pip install -r requirements.txt --upgrade

# pull the latest code from the repository
git pull origin main

# restart the service
sudo systemctl restart polkabot.service