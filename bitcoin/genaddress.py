# -*- coding: utf-8 -*-

import codecs
import hashlib
import mpmath as mp
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
    mp.dps = 1000
    b58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

    def base58_to_dec(addr):
        dec = 0
        for i in range(len(addr)):
            dec = int(dec * 58 + b58.index(addr[i]))
        return(dec)

    def dec_to_byte(dec):
        out = ''
        while dec != 0:
            remn = mp.mpf(dec % 256)
            dec = mp.mpf((dec - remn) / 256)
            temp = hex(int(remn))
            if len(temp) == 3:
                temp = '0' + temp[-1]
            else:
                temp = temp[2:]
            out = temp + out

        return (out)

    dec = base58_to_dec(addr)
    out = dec_to_byte(dec)
    return (out)

if __name__ == '__main__':
    key = sys.argv[1]
    if len(key) < 32:
        key = '0' * (32 - len(key)) + key
    print(key)
    gen_address(key)
