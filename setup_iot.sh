#!/bin/bash

sudo apt update
sudo apt upgrade
sudo apt-get install -y apache2
sudo apt-get install -y git
sudo apt-get install -y build-essential
sudo apt-get install -y libcurl4-openssl-dev
sudo apt-get install -y libsqlite3-dev
sudo apt-get install -y pkg-config
sudo apt-get install -y curl
sudo apt-get install -y gphoto2
sudo apt-get install -y python3
curl -L https://raw.github.com/pageauc/rclone4pi/master/rclone-install.sh | bash
sudo git clone https://github.com/mariolopez2/New_IoT
sudo python3 /home/pi/New_IoT/setup.py