# -*- coding: utf-8 -*-

from sys import byteorder, argv
from hashlib import sha256

## You can put in $data an 80-byte block header to get its header hash,
## or a raw transaction to get its txid

if __name__ == '__main__':
    #data = "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff0704ffff001d014dffffffff0100f2052a01000000434104e70a02f5af48a1989bf630d92523c9d14c45c75f7d1b998e962bff6ff9995fc5bdb44f1793b37495d80324acba7c8f537caaf8432b8d47987313060cc82d8a93ac00000000"
    data = "010000000126c07ece0bce7cda0ccd14d99e205f118cde27e83dd75da7b141fe487b5528fb000000008b48304502202b7e37831273d74c8b5b1956c23e79acd660635a8d1063d413c50b218eb6bc8a022100a10a3a7b5aaa0f07827207daf81f718f51eeac96695cf1ef9f2020f21a0de02f01410452684bce6797a0a50d028e9632be0c2a7e5031b710972c2a3285520fb29fcd4ecfb5fc2bf86a1e7578e4f8a305eeb341d1c6fc0173e5837e2d3c7b178aade078ffffffff02b06c191e010000001976a9143564a74f9ddb4372301c49154605573d7d1a88fe88ac00e1f505000000001976a914010966776006953d5567439e5e39f86a0d273bee88ac00000000"
    hash = sha256(sha256(data.decode('hex')).digest()).digest()

    print("Warning: this code only tested on a little-endian x86_64 arch")
    print("\n")
    print("System byte order:", byteorder)
    print("Internal-Byte-Order Hash: ", hash.encode('hex_codec'))
    print("RPC-Byte-Order Hash:      ", hash[::-1].encode('hex_codec'))
