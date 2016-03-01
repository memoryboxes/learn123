bpc-client
=============

Python client library for crossflow bpc APIs

tools
-------
python bin/bpccurl.py -h

exp:

    python bin/bpccurl.py trans "{'earliest':'2012-12-04T19:15:00','latest':'2012-12-04T19:16:00','view_name':'app1','cap_name':'cap1'}" --host xxxx
    python bin/bpccurl.py multitrans "{'earliest':'2012-12-04T19:15:00','latest':'2012-12-04T19:16:00','view_name':'app1','cap_name':'cap1','fields':['trans_channel','ip_dst','ip_src','ret_code']}" --host xxxx
    python bin/bpccurl.py stats "{'earliest':'2012-12-04T19:15:00','latest':'2012-12-04T19:17:00','view_name':'app1','cap_name':'cap1'}" --host xxxx
    python bin/bpccurl.py baseline "{'earliest':'2012-12-11T19:15:00','latest':'2012-12-11T19:20:00','view_name':'app1','cap_name':'cap2'}" --host xxxx
    python bin/bpccurl.py alert "{'earliest':'2015-04-29T16:00:00','latest':'2015-04-29T16:01:00','view_name':'app1','cap_name':'cap2'}" --host xxxx
    python bin/bpccurl.py baseline "{'earliest':'2012-12-11T19:15:00','latest':'2012-12-11T19:20:00','view_name':'app1','cap_name':'cap2'}" --host xxxx --token test


Release Note:

2015-05-26 version 1.1.0
===================================
for new trans


2015-01-23 version 1.0.0
===================================
perfect alerts tests
