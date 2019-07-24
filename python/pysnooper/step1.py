# -*- coding: utf-8 -*-

import pysnooper


@pysnooper.snoop()
def number_to_bits(number):
    if number:
        bits = []
        while number:
            number, remainder = divmod(number, 2)
            bits.insert(0, remainder)
        return bits
    else:
        return [0]


if __name__ == '__main__':
    number_to_bits(6)
