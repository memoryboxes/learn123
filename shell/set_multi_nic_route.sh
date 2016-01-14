#!/bin/bash

ip route add default via 172.16.14.1 dev eth0
ip route add default via 172.16.14.1 dev eth0 table rteth0
ip rule add from 172.16.14.24 table rteth0
ip route add default via 172.16.13.1 dev eth1 table rteth1
ip rule add from 172.16.13.24 table rteth1
ip route flush cache
