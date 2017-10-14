#!/bin/bash

# This will fix the wireless adaptor when running Kali natively on on a Macbook. Tested on Macbook Air 2012, but would work on
# similar models as well. Run:
#       lsci
# to identify your model and fix the script.

apt update -y
apt install linux-headers-$(uname -r | sed 's,[^-]*-[^-]*-,,') broadcom-sta-dkms -y
modprobe -r b44 b43 b43legacy brcmsmac
modprobe wl

# The following will fix the issue of the tilde key not working properly
echo "echo 0 > /sys/module/hid_apple/parameters/iso_layout" >>/etc/rc.local

# My Mac had issues waking up immediately after suspend, with the lid still closed.
# The follow process will fix that, and perhaps also improve battery life.
apt install powertop -y
echo "powertop --auto-tune" >> /etc/rc.local
echo "exit 0" >> /etc/rc.local
