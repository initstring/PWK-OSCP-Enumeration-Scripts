#!/bin/bash

################ Set up some variables ################
HOSTNAME=workstation01
################  Done with variables  ################

# Change the password
passwd

# Change the hostname (kali looks suspicious on a network)
echo $HOSTNAME > /etc/hostname
hostname $HOSTNAME

# General updates
apt update; apt upgrade -y;

# Get Metasploit ready
systemctl enable postgresql; systemctl start postgresql
msfdb init
echo exit | msfconsole                                                 # sets up the needed .msf4 folder
echo "spool /root/msf_console.log" > /root/.msf4/msfconsole.rc         # enables logging of all msf activity

# Set up Docker
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
echo "deb https://download.docker.com/linux/debian stretch stable" >> /etc/apt/sources.list 
apt update
apt install docker-ce -y

# Install node-js
apt install nodejs npm -y

# Install aquatone for bounty recon
gem install aquatone

# Set directory to store custom scripts
mkdir /root/scripts

# Grab some good open source scripts, etc
git clone https://github.com/danielmiessler/SecLists.git /opt/seclists
git clone https://github.com/jhaddix/domain; /opt/enumall
git clone https://github.com/wireghoul/graudit.git /opt/graudit

# TOOL - HTTPScreenShot
apt install python-selenium -y
git clone https://github.com/breenmachine/httpscreenshot.git /opt/httpscreenshot
cd /opt/httpscreenshot
chmod 700 install-dependencies.sh && ./install-dependencies.sh

# TOOL - smbexec
git clone https://github.com/pentestgeek/smbexec.git /opt/smbexec
cd /opt/smbexec
echo 1 | ./install.sh                                     # installs for Debian-based system
echo 4 | ./install.sh                                     # Need to run second time to compile binaries

# TOOL - gitrob
git clone https://github.com/michenriksen/gitrob.git /opt/gitrob
gem install bundler
su postgres
createuser -s gitrob --pwprompt
createdb -O gitrob gitrob
exit
cd /opt/gitrob/bin
gem install gitrob

# TOOL - CMSmap
git clone https://github.com/Dionach/CMSmap /opt/CMSmap

# TOOL - EyeWitness
apt install eyewitness -y

# TOOL - printer exploits
git clone https://github.com/MooseDojo/praedasploit /opt/praedasploit

# TOOL - discovery scripts
git clone https://github.com/leebaird/discover.git /opt/discover
cd /opt/discover && ./update.sh

# TOOL - beef
cd /opt/
wget https://raw.githubusercontent.com/beefproject/beef/a6a7536e/install-beef
chmod 700 ./install-beef
echo y | ./install-beef
rm -f ./install-beef

# TOOL - DSHashes
wget https://storage.googleapis.com/google-code-archive-source/v2/code.google.com/ptscripts/source-archive.zip and move dshashes.py to /opt/NTDSXtract/dshashes.py -O /opt/NTDSXtract/dshashes.py

# TOOL - nosqlmap
git clone https://github.com/tcstool/NoSQLMap.git /opt/NoSQLMap

# TOOL - spiderfoot
mkdir /opt/spiderfoot/ && cd /opt/spiderfoot
wget http://sourceforge.net/projects/spiderfoot/files/spiderfoot-2.3.0-src.tar.gz/download
tar xzvf download
pip install lxml
pip install netaddr
pip install M2Crypto
pip install cherrypy
pip install mako

# TOOL - various powershell
git clone https://github.com/mattifestation/PowerSploit.git /opt/PowerSploit
cd /opt/PowerSploit && wget https://raw.githubusercontent.com/obscuresec/random/master/StartListener.py && wget https://raw.githubusercontent.com/darkoperator/powershell_scripts/master/ps_encoder.py
git clone https://github.com/samratashok/nishang /opt/nishang

# TOOL - veil framework
git clone https://github.com/Veil-Framework/Veil.git /opt/veil
cd /opt/veil/setup
./setup.sh -c

# TOOL - netcreds
git clone https://github.com/DanMcInerney/net-creds.git /opt/net-creds

# TOOL- wifiphisher
apt install wifiphisher -y

# TOOL - phishing-frenzy
git clone https://github.com/pentestgeek/phishing-frenzy.git /var/www/phishing-frenzy

# TOOL - custom list of tools/scripts
git clone https://github.com/macubergeek/gitlist.git /opt/gitlist

# TOOL - flash decompiler
wget https://www.free-decompiler.com/flash/download/ffdec_10.0.0.deb
apt install ./ffdec_10.0.0.deb -y                                                       # for editing the swf packages
rm -f ./ffdec_10.0.0.deb
mkdir /root/scripts/flash-stuff; cd /root/scripts/flash-stuff
wget https://fpdownload.macromedia.com/get/flashplayer/updaters/27/playerglobal27_0.swc # required to edit scripts inline

# Some custom scripts from the great "Hacker's Playbook"
git clone https://github.com/cheetz/Easy-P.git /opt/easy-p
git clone https://github.com/cheetz/Password_Plus_One /opt/password_plus_one
git clone https://github.com/cheetz/PowerShell_Popup /opt/powershell_popup
git clone https://github.com/cheetz/icmpshock /opt/icmpshock
git clone https://github.com/cheetz/brutescrape /opt/brutescrape
git clone https://www.github.com/cheetz/reddit_xss /opt/reddit_xss

# Some forked vesions of PowerSploit and PowerTools
git clone https://github.com/initstring/PowerSploit.git /opt/powersploit
git clone https://github.com/initstring/PowerTools.git /opt/powertools
git clone https://github.com/initstring/nishang.git /opt/nishang
