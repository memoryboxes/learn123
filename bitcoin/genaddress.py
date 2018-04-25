# -*- coding: utf-8 -*-

import codecs
import hashlib
import os
import sys
from pycoin import ecdsa, encoding

def gen_address(private_key):
    #private_key = codecs.encode(os.urandom(32), 'hex').decode()
    secret_exponent= int('0x'+private_key, 0)
    print('WIF: ' + encoding.secret_exponent_to_wif(secret_exponent, compressed=False))
    public_pair = ecdsa.public_pair_for_secret_exponent(ecdsa.secp256k1.generator_secp256k1, secret_exponent)
    print(public_pair)
    hash160 = encoding.public_pair_to_hash160_sec(public_pair, compressed=True)
    print("hash160: {}".format(hash160.hex()))
    print("Bitcoin address: {}".format(encoding.hash160_sec_to_bitcoin_address(hash160)))

def decode(addr):
    b58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    decoded = ''
    for i in addr:
        temp = hex(b58.index(i))
        if len(temp) == 3:
            temp = '0' + temp[-1]
        else:
            temp = temp[2:]
        decoded += (temp)
    return (decoded)

if __name__ == '__main__':
    key = sys.argv[1]
    if len(key) < 32:
        key = '0' * (32 - len(key)) + key
    print(key)
    gen_address(key)
