#!/bin/bash

URL=https://weakpass.com/lists
CUTS=`echo ${URL#http://} | awk -F '/' '{print NF -2}'`
wget -r -l1 -nH --cut-dirs=${CUTS} --no-parent -A.torrent --no-directories -R robots.txt ${URL}
