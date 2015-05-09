#!/bin/bash
ifconfig|grep -oE "inet addr.*Bcast"|sed -e 's/inet addr://g' -e 's/\s.*Bcast//g'
