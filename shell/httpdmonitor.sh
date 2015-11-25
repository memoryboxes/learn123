#/bin/bash
CURRENT_LOAD=`top -b -n 1|grep 'load average'|awk '{print $12}'|sed 's/,//'`
declare -i current_load=${CURRENT_LOAD%.*}
if [ $current_load -gt 20 ]; then
    echo "LOAD AVERAGE TO HIGH:"$CURRENT_LOAD
    service httpd restart
fi
