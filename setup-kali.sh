#!/bin/bash

##### NOTE: RUN THIS FROM A TERMINAL WIHIN A GUI SESSION (WINE DEPS) ####
#####     Last tested with Kali 2017.2. Use at your own risk!        ####

echo "You should be launching the from the terminal within a desktop session, as some of the scripts launch GUI commands..."
read -p "Press enter to continue"

echo "Setting a new root password..."
passwd

read -p "Let's set a new hostname: " HOSTNAME
echo "Setting the hostname to $HOSTNAME - kali sounds shady in logs..."
echo $HOSTNAME > /etc/hostname
hostname $HOSTNAME

echo "Configuring text-based address bar in file browser..."
gsettings set org.gnome.nautilus.preferences always-use-location-entry true

echo "Setting up a /root/scripts/ directory for you..."
mkdir /root/scripts

echo "Updating ruby..."
gem update --system

echo "Starting github clones..."
cd /opt/
for repo in \
    leebaird/discover                 `# Nice DNS/human recon tool with integrated HTML report output` \
    danielmiessler/SecLists           `# Wordlists for DNS, passwords, users, fuzzing, etc` \
    fuzzdb-project/fuzzdb             `# More wordlists!` \
    jhaddix/domain                    `# Sub-domain enumeration tool` \
    wireghoul/graudit                 `# greo auditing for source code review` \
    pentestgeek/phishing-frenzy       `# Phishing framework with nice web UI` \
    tcstool/NoSQLMap                  `# MongoDB and CouchDB scanning and exploitation` \
    DanMcInerney/net-creds            `# Scans pcap files for passwords and hashes` \
    PowerShellMafia/PowerSploit       `# PowerShell post-exploitation framewok` \
    samratashok/nishang               `# PowerShell tools for all phases of the pentest` \
    breenmachine/httpscreenshot       `# Rapid remote screenshot gatherer` \
    brav0hax/smbexec                  `# A rapid psexec style attack with samba tools` \
    cheetz/Easy-P                     `# auto-generates commong PowerShell commands` \
    cheetz/PowerShell_Popup           `# PowerShell script to create pop up prompting user for password` \
    codingo/VHostScan                 `# Discovers virtual web hosts on a server` \
  ;do \
  echo "Cloning $repo..."; \
  git clone https://github.com/$repo.git; \
done

echo "Configuring the discovery scripts, which also updates the distro..."
cd /opt/discover && ./update.sh

echo "Downloading neo4j for you, as prompted by the discovery install..."
cd /opt
wget https://neo4j.com/artifact.php?name=neo4j-community-3.2.5-unix.tar.gz -O ./neo4j.tar.gz
tar -xf ./neo4j.tar.gz
rm -f ./neo4j.tar.gz

echo "Configuring Veil framework..."
# Note: already installed in the discovery script above. If not, you can run:
# git clone https://github.com/Veil-Framework/Veil.git /opt/Veil
cd /opt/Veil/setup
./setup.sh -c

echo "Preparing Metasploit..."
systemctl enable postgresql; systemctl start postgresql
msfdb init
echo exit | msfconsole                                                 # sets up the needed .msf4 folder
echo "spool /root/msf_console.log" > /root/.msf4/msfconsole.rc         # enables logging of all msf activity

echo "Setting up Docker..."
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
echo "deb https://download.docker.com/linux/debian stretch stable" >> /etc/apt/sources.list
apt update
apt install docker-ce -y

echo "Installing tools with easy installs..."
apt install wifiphisher openvas -y
gem install aquatone

echo "Installing HTTPScreenShot..."
apt install python-selenium -y
cd /opt/httpscreenshot
chmod 700 install-dependencies.sh && ./install-dependencies.sh

echo "Installing some messy requirements for smbexec..."
cd /tmp
wget https://github.com/libyal/libesedb/releases/download/20170121/libesedb-experimental-20170121.tar.gz
tar -xzvf ./libesedb-experimental-20170121.tar.gz
cd libesedb-20170121
CFLAGS="-g -O2 -Wall -fgnu89-inline" ./configure --enable-static-executables
make
mv esedbtools /opt/esedbtools

echo "Configuring smbexec..."
wget https://github.com/interference-security/ntds-tools/raw/master/ntdsxtract_v1_0.zip -O /tmp/ntds.zip
unzip /tmp/ntds.zip -d /tmp/
mv "/tmp/NTDSXtract 1.0" /opt/NTDSXtract
apt-get install automake autoconf autopoint gcc-mingw-w64-x86-64 libtool pkg-config
echo 1 | /opt/smbexec/install.sh

echo "Getting DSHashes script, we need it for smbexec..."
cd /tmp
wget https://storage.googleapis.com/google-code-archive-source/v2/code.google.com/ptscripts/source-archive.zip
unzip ./source-archive.zip
mkdir /opt/NTDSXtract
cp /tmp/ptscripts/trunk/dshashes.py /opt/NTDSXtract/

echo "Installing spiderfoot, another OSINT tool..."
wget http://sourceforge.net/projects/spiderfoot/files/spiderfoot-2.11.0-src.tar.gz/download -O /tmp/spider.tar.gz
tar xzvf /tmp/spider.tar.gz -C /opt/
pip install lxml
pip install netaddr
pip install M2Crypto
pip install cherrypy
pip install mako
rm -f /tmp/spider.tar.gz

echo "Installing a flash decompiler, ff-dec..."
cd /tmp
wget https://www.free-decompiler.com/flash/download/ffdec_10.0.0.deb
apt install ./ffdec_10.0.0.deb -y
rm -f ./ffdec_10.0.0.deb
mkdir /opt/flash-stuff; cd /opt/flash-stuff
wget https://fpdownload.macromedia.com/get/flashplayer/updaters/27/playerglobal27_0.swc

echo "Installing jython2.7 for use with Burp..."
cd /tmp
wget https://repo1.maven.org/maven2/org/python/jython-installer/2.7.0/jython-installer-2.7.0.jar
java -jar /tmp/jython-installer-2.7.0.jar -s -d /opt/jython


echo "Configuring gitrob..."
apt install libpq-dev -y zlib1g-dev
runuser -l postgres -c 'createuser -s gitrob --pwprompt'
runuser -l postgres -c 'createdb -O gitrob gitrob'
gem install gitrob

echo "Preparing gitrob... provide the password from earlier"
gitrob --configure

echo "All done, yay!"
