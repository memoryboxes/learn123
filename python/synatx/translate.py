# -*- coding: utf-8 -*-

""" for python3 translate func title change
"""
table = str.maketrans(dict.fromkeys('0123456789'))
print('123hello.jpg'.translate(table))


table = str.maketrans('0123', 'abcd')
print('123hello.jpg'.translate(table))

