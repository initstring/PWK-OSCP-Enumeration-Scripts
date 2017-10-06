#!/bin/bash

# This will fix the wireless adaptor when running Kali natively on on a Macbook. Tested on Macbook Air 2012, but would work on
# similar models as well. Run:
#       lsci
# to identify your model and fix the script.

apt update -y
apt install linux-headers-$(uname -r | sed 's,[^-]*-[^-]*-,,') broadcom-sta-dkms -y
modprobe -r b44 b43 b43legacy brcmsmac
modprobe wl