#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from sets import Set
from .container import ContainerList

ip_pool = Set(["172.16.13.{}/24".format(i) for i in xrange(20,40)])

def get_free_ips():
    """
        return ["172.16.1.1", ...]
        return [] if has none free ip
    """

    all_containers = ContainerList.get()
    ips = Set([container['eths'][2] for container in all_containers])
    return sorted(list(ip_pool - ips))

