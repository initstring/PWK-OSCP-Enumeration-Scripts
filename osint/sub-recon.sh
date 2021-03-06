#!/bin/bash

# This script uses well-known subdomain enumeration tools.
# Wordlist is created on the fly by combining a good list with additional words from target's website.
# Output is formatted in a way I prefer.

########    PLEASE SET UP VARIABLES HERE    ########
OUTDIR=~/osint           # We will create subfolders for each domain here
WORDLIST=/opt/SecLists/Discovery/DNS/sortedcombied-knock-dnsrecon-fierce-reconng.txt # Big wordlist to combine with custom one
EADIR=/opt/domain              # https://github.com/jhaddix/domain
########    YAY, ALL DONE WITH VARIABLES    ########

read -p 'Enter TLD for subdomain enumeration (example: uber.com): ' RECON_DOMAIN
read -p 'Enter full URL to scrape a wordlist from (example: https://uber.com/au) ' RECON_URL

# set up the directory structure
mkdir -p $OUTDIR/$RECON_DOMAIN/dns-recon

# change into dir - as output files from enumall go to local dir
cd $OUTDIR/$RECON_DOMAIN/dns-recon

# create a custom wordlist combining a scrape of the full URL plus a nice hefty SecLists file
cewl -v --depth 1 -m 4 $RECON_URL \
  -w $OUTDIR/$RECON_DOMAIN/cewl-wordlist.txt
cat $WORDLIST $OUTDIR/$RECON_DOMAIN/cewl-wordlist.txt > /tmp/$RECON_DOMAIN-wordlist.txt

# run the consolidated recon
python $EADIR/enumall.py $RECON_DOMAIN -w /tmp/$RECON_DOMAIN-wordlist.txt

# try a DNS zone transfer
for i in $(host -t ns $RECON_DOMAIN | cut -d " " -f 4); \
  do host -l $RECON_DOMAIN $i \
  >> $OUTDIR/$RECON_DOMAIN/dns-recon/zone-transfer.txt; \
done

# convert everything to lowercase
cat $RECON_DOMAIN.csv | tr '[:upper:]' '[:lower:]' \
  > $OUTDIR/$RECON_DOMAIN/dns-recon/$RECON_DOMAIN-lowercase.csv

# remove out of scope domains
cat $RECON_DOMAIN-lowercase.csv | grep $RECON_DOMAIN \
 > $OUTDIR/$RECON_DOMAIN/dns-recon/$RECON_DOMAIN-scope.csv

# make a list of all unique hostnames
cat $RECON_DOMAIN-scope.csv | cut -d '"' -f 2 | sort | uniq -i | grep $RECON_DOMAIN \
  > $OUTDIR/$RECON_DOMAIN/dns-recon/hostnames.txt

# make a list of all unique IP addresses
cat $RECON_DOMAIN-scope.csv | cut -d '"' -f 4 | grep . | sort | uniq -i \
  > $OUTDIR/$RECON_DOMAIN/dns-recon/ip-list.txt

# make a list of IP addresses with DNS count
cat $RECON_DOMAIN-scope.csv | cut -d '"' -f 4 | grep . | sort | uniq -i -c \
  | cut -d ' ' -f 7- \
  > $OUTDIR/$RECON_DOMAIN/dns-recon/ip-count.txt
