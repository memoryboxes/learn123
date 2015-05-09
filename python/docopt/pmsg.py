#!/bin/env python
# -*- coding: utf-8 -*-
"""Pktminer2 msg send tools

Usage:
  pmsg run (start|stop) <interface> [--action==(all|store|pring|compress|heartbeat|filter)]
  pmsg get <interface> [--status==(pktminer|eth)]
  pmsg reset <interface>
  pmsg refilter <interface>

Options:
  -h --help                                             Show this screen.
  --version                                             Show version.
  --action==(store|pring|compress|heartbeat|filter)     (start|stop) (store|pring...) [default: all]
  --status=(pktminer|eth)                               get status [default: pktminer]

"""
from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Pmsg 2.0')
    print arguments
