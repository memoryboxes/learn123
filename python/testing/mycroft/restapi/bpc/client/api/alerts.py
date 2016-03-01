# -*- coding: utf-8 -*-

from datetime import datetime

from .base import BPCRestfulAPIBase, BPCRestfulResultsBase
from .base import BPC_RESTFUL_PARAM_NONE

class Alerts(BPCRestfulAPIBase):

    def __repr__(self):
        return '<BPCRestfulAPI Alerts>'

    def __init__(self, auth_checker,
                 earliest = datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                 latest = datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                 limit=100, offset=0, sort='ts+DESC',
                 view_name=BPC_RESTFUL_PARAM_NONE,
                 cap_name=BPC_RESTFUL_PARAM_NONE,
                 alert_type=BPC_RESTFUL_PARAM_NONE,
                 alert_scope=BPC_RESTFUL_PARAM_NONE,
                 indicator=BPC_RESTFUL_PARAM_NONE,
                 status=BPC_RESTFUL_PARAM_NONE):
        """Fetches alerts rows

        Args:
            earliest -- latest:  alerts time scope, support ISO8601, exp:'2015-01-01T00:00:00'

            limit: return rows limit per request. limit should in range (0, 1000])

            view_name: app1

            cap_name: intf2

            alert_type(en-us): 'thresholds' | 'ret_code'   | 'baseline' | 'located_error'
            alert_type(zh-cn): '阈值告警'   | '返回码告警' | '基线告警' | '故障定位'

            alert_scope(en-us): 'SPV' | 'cap'  | 'site' | 'server'
            alert_scope(zh-cn): 'SPV' | '组件' | '站点' | '主机'

            indicator(en-us): 'duration' | 'trans_count' | 'rr_rate' | 'succ_rate'
            indicator(zh-cn): '响应时间' | '交易量'      | '响应率'  | '成功率'

            status(en-us): 'last'   | 'relieve'
            status(zh-cn): '持续中' | '已恢复'
        """
        super(Alerts, self).__init__(auth_checker)

        self._params = {
                          'earliest': earliest,
                          'latest': latest,
                          'limit': limit,
                          'offset': offset,
                          'sort': sort,
                          'view_name': view_name,
                          'cap_name': cap_name,
                          'type': alert_type,
                          'scope': alert_scope,
                          'indicator': indicator,
                          'status': status
                       }

    def get_total_records(self):
        return [item for item in self.iter_records()]

    def get_total_raw_records(self):
        return [item for item in self.iter_raw_records()]

    def get_total_count(self):
        return len(self.iter_raw_records())

    def iter_records(self):
        """Fetches alerts rows

        Returns:
            record iterator

        Raises:
            BPCRestfulAuthError: An error occurred accessing restful token auth
            BPCRestfulAPIError: An error occurred accessing restful api requests
        """

        for group_records in self.iter_raw_records():
            for record in group_records.json.get('items', []):
                yield record

    def iter_raw_records(self):
        """Fetches raw alerts rows

        Returns:
            BPCRestfulResultsBase instance

        Raises:
            BPCRestfulAuthError: An error occurred accessing restful token auth
            BPCRestfulAPIError: An error occurred accessing restful api requests
        """

        return BPCRestfulResultsBase(self.auth_checker, self._get('alerts/', **self._params))
