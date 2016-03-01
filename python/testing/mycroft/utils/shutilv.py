#!/usr/bin/env python
#  -*- coding: utf-8 -*-

def strip_folders(folders):
    return [item for item in folders if not item.startswith('.')]
