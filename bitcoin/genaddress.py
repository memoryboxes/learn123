# -*- coding: utf-8 -*-

import codecs
import hashlib
import os
import sys
from pycoin import ecdsa, encoding

def gen_address(private_key):
    secret_exponent= int('0x'+private_key, 0)
    print('WIF: ' + encoding.secret_exponent_to_wif(secret_exponent, compressed=False))
    public_pair = ecdsa.public_pair_for_secret_exponent(ecdsa.secp256k1.generator_secp256k1, secret_exponent)
    print(public_pair)
    hash160 = encoding.public_pair_to_hash160_sec(public_pair, compressed=True)
    print('Bitcoin address: %s' % encoding.hash160_sec_to_bitcoin_address(hash160))

if __name__ == '__main__':
    #key = codecs.encode(os.urandom(32), 'hex').decode()
    key = sys.argv[1]
    if len(key) < 32:
        key = '0' * (32 - len(key)) + key
    print(key)
    gen_address(key)
