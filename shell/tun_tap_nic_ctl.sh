#!/bin/bash
#
# config_tap          Start up the tun/tap virtual nic
#
# chkconfig: 2345 55 25

USER="root"
TAP_NETWORK="192.168.1."
declare -a eths=(10 11 12 13)
DESC="TAP config"

do_start() {
  if [ ! -x /usr/sbin/tunctl ]; then
    echo "/usr/sbin/tunctl was NOT found!"
    exit 1
  fi
  for addr in "${eths[@]}"; do
    tunctl -t eth$addr -u root
    ifconfig eth$addr ${TAP_NETWORK}${addr}  netmask 255.255.255.0 promisc
    ifconfig eth$addr
  done;
}

do_stop() {
  for addr in "${eths[@]}"; do
    ifconfig eth$addr down
  done;
}
do_restart() {
  do_stop
  do_start
}
check_status() {
  for addr in "${eths[@]}"; do
    ifconfig eth$addr
  done;
}

case $1 in
  start)    do_start;;
  stop)     do_stop;;
  restart)  do_restart;;
  status)
            echo "Status of $DESC: "
            check_status
            exit "$?"
            ;;
  *)
	echo "Usage: $0 {start|stop|restart|status}"
	exit 1
esac
