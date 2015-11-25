#!/usr/bin/env python
#  -*- coding: utf-8 -*-
import pprint
from collections import defaultdict

records = [
        {"Ip":1, "PktLen":2, "PktCnt": 3},
        {"Ip":1, "PktLen":2, "PktCnt": 3},
        {"Ip":2, "PktLen":2, "PktCnt": 3},
        {"Ip":3, "PktLen":2, "PktCnt": 3},
        {"Ip":5, "PktLen":2, "PktCnt": 3},
        {"Ip":1, "PktLen":2, "PktCnt": 3, "Pktzz": 4},
    ]

from itertools import groupby

new_records = []
for k, g in groupby(sorted(records, key=lambda x:x['Ip']), lambda x:x['Ip']):
    new_record = {}
    for record in g:
        for kk, v in record.iteritems():
            if kk not in new_record.keys():
                new_record.setdefault(kk, v)
            else:
                if kk != 'Ip':
                    new_record[kk] += v
    new_records.append(new_record)

pprint.pprint(new_records)

