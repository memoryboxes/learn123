# -*- coding: utf-8 -*-

import sys
from hashlib import *
from base58 import *

def SHA256D(bstr):
    return sha256(sha256(bstr).digest()).digest()

def ConvertPKHToAddress(prefix, addr):
    data = prefix + addr
    return b58encode(data + SHA256D(data)[:4])

def PubkeyToAddress(pubkey_hex):
    pubkey = bytearray.fromhex(pubkey_hex)
    round1 = sha256(pubkey).digest()
    h = new('ripemd160')
    h.update(round1)
    pubkey_hash = h.digest()
    return ConvertPKHToAddress(b'\x00', pubkey_hash)

if __name__ == '__main__':
    # pubkey = "044da006f958beba78ec54443df4a3f52237253f7ae8cbdb17dccf3feaa57f3126da0a0909f11998130c2d0e86a485f4e79ee466a183a476c432c68758ab9e630b"
    pubkey = sys.argv[1]

    print(len(pubkey))
    print("Address: %s" % PubkeyToAddress(pubkey))
