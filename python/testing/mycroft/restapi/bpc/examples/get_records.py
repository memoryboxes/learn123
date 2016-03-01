# -*- coding: utf-8 -*-

import os
import sys
import json

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(TEST_DIR)
sys.path.insert(0, ROOT_DIR)

from client import BPCRestfulClient
client = BPCRestfulClient(api_endpoint = 'http://127.0.0.1/api/')

def show_alerts():
    alert_records = client.alerts(earliest='2015-02-02T14:00:00',
                                  latest='2015-02-02T15:00:00',
                                  limit=10,
                                  view_name='app1',
                                  cap_name='cap2',
                                  alert_type='阈值告警',
                                  indicator='响应时间',
                                  sort='ts_start+ASC,peak+DESC',
                                  status='已恢复').get_total_records()
    print json.dumps(alert_records, ensure_ascii=False, indent=4)

def show_baselines():
    baseline_records = client.baselines(earliest='2015-01-28T15:00:00',
                                        latest='2015-01-29T10:10:00',
                                        view_name='app1',
                                        cap_name='cap2').get_total_records()
    print json.dumps(baseline_records, ensure_ascii=False, indent=4)

def show_stats():
    stats_records = client.stats(earliest='2012-12-04T19:00:00',
                                 latest='2012-12-04T19:01:00',
                                 view_name='app1',
                                 cap_name='cap1',
                                 dimensions=['ip_src'],
                                 indicators=['trans_count'],
                                 stats_filter={'trans_count' :{'$gte':10}}).get_total_records()
    print json.dumps(stats_records, ensure_ascii=False, indent=4)

def show_trans():
    trans_records = client.trans(earliest='2012-12-04T19:00:00',
                                 latest='2012-12-04T19:01:00',
                                 view_name='app1',
                                 cap_name='cap1',
                                 fields=['trans_channel', 'ip_dst', 'ip_src', 'ret_code', 'earliest'],
                                 trans_filter={}).get_total_records()
    print json.dumps(trans_records, ensure_ascii=False, indent=4)

def show_multi_trans():
    multi_trans_records = client.multi_trans(
                                        earliest='2012-12-04T19:00:00',
                                        latest='2012-12-04T19:01:00',
                                        view_name='app1',
                                        cap_name='cap2',
                                        fields=['transaction_id', 'DestIp', 'SrcIp', 'ret_code', 'ts', 'PanHash'],
                                        trans_filter={'ip_dst':'10.1.165.134'},
                                        search_timeout=180).get_total_records()
    print json.dumps(multi_trans_records, ensure_ascii=False, indent=4)

def show_iter_trans_record():
    trans_records = client.trans(earliest='2015-07-10T19:00:00',
                                 latest='2015-07-10T19:01:00',
                                 view_name='app1',
                                 cap_name='cap1',
                                 fields=['trans_channel', 'ip_dst', 'ip_src', 'ret_code', 'earliest'],
                                 trans_filter={}).iter_records()

    for record in trans_records:
        print json.dumps(record, ensure_ascii=False, indent=4)

def show_iter_raw_trans_record():
    trans_records = client.trans(earliest='2015-07-10T19:00:00',
                                 latest='2015-07-10T19:00:10',
                                 view_name='app1',
                                 cap_name='cap1',
                                 fields=['trans_channel', 'ip_dst', 'ip_src', 'ret_code', 'earliest'],
                                 trans_filter={}).iter_raw_records()

    for record in trans_records:
        print record

if __name__ == '__main__':
    show_alerts()
    show_baselines()
    show_stats()
    show_trans()
    show_multi_trans()
    show_iter_trans_record()
    show_iter_raw_trans_record()
