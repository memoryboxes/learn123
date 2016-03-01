# -*- coding: utf-8 -*-

from .alerts import Alerts
from .baselines import Baselines
from .stats import Stats
from .trans import Trans, MultiTrans
from .alertts import Alertts

class BPCRestfulAPI(object):

    def __repr__(self):
        return '<BPCClient API>'

    def alerts(self, **params):
        return Alerts(self.auth_checker, **params)

    def baselines(self, **params):
        return Baselines(self.auth_checker, **params)

    def stats(self, **params):
        return Stats(self.auth_checker, **params)

    def trans(self, **params):
        return Trans(self.auth_checker, **params)

    def multi_trans(self, **params):
        return MultiTrans(self.auth_checker, **params)

    def alertts(self, **params):
        return Alertts(self.auth_checker, **params)