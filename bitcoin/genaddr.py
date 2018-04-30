# -*- coding: utf-8 -*-

"""doctopt msg send tools

Usage:
  genaddr.py p2addr     <private>
  genaddr.py addr2160   <addr>
  genaddr.py 1602addr   <160>
  genaddr.py addrfile2160 <fileaddr>

Options:
  -h --help                                             Show this screen.
  --version                                             Show version.

Example:

    genaddr.py p2addr 6bd3b27c591                                         # gen address from private 0x6bd3b27c591->1PiFuqGpG8yGM5v6rNHWS3TjsG6awgEGA1
    genaddr.py addr2160 1PiFuqGpG8yGM5v6rNHWS3TjsG6awgEGA1                # gen hash160 from address PiFuqGpG8yGM5v6rNHWS3TjsG6awgEGA1->f92044c7924e58000000000000000000000000000000001e
    genaddr.py 1602addr f92044c7924e58000000000000000000000000000000001e  # gen address from hash160 f92044c7924e58000000000000000000000000000000001e->PiFuqGpG8yGM5v6rNHWS3TjsG6awgEGA1


    echo -n 'Money is the root of all evil.'|sha256sum => get private key is d1bb6f97f53377cadd8d3230f8f542a91d0055b87ec7e69c53c7b48dc51e8cfb => hash160:d1bb6f97f53377cadd8d3230f8f542a91d0055b87ec7e69c53c7b48dc51e8cfb
    genaddr.py 1602addr 8b0a993126c3bf8f4b28c8264b553d6aa39f2956          # gen address from hash160 8b0a993126c3bf8f4b28c8264b553d6aa39f2956>1DgBd4AgrBrzk4JnxVFH8hJmx9a3Jownqh
"""

from pycoin import ecdsa, encoding
from docopt import docopt


def gen_address(private_key):
    # private_key = codecs.encode(os.urandom(32), 'hex').decode()
    secret_exponent= int('0x' + private_key, 0)
    print('WIF: ' + encoding.secret_exponent_to_wif(secret_exponent, compressed=False))
    public_pair = ecdsa.public_pair_for_secret_exponent(ecdsa.secp256k1.generator_secp256k1, secret_exponent)
    print('public pair:', public_pair)
    hash160 = encoding.public_pair_to_hash160_sec(public_pair, compressed=True)
    print("hash160: {}".format(hash160.hex()))
    print("Bitcoin address: {}".format(encoding.hash160_sec_to_bitcoin_address(hash160, address_prefix=b'\0')))


def gen_address_from_160(hash160):
    return encoding.hash160_sec_to_bitcoin_address(bytes.fromhex(hash160))


def decode(addr):
    return encoding.bitcoin_address_to_hash160_sec(addr).hex()


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Pmsg 2.0')

    if arguments['p2addr']:
        key = arguments['<private>']
        if len(key) < 32:
            key = '0' * (32 - len(key)) + key
        print('private:', key)
        gen_address(key)
    elif arguments['addr2160']:
        key = arguments['<addr>']
        print('address:', key)
        print(decode(key))
    elif arguments['1602addr']:
        key = arguments['<160>']
        print('hash160:', key)
        print("Bitcoin address:{}".format(gen_address_from_160(key)))
    elif arguments['addrfile2160']:
        fileaddr = arguments['<fileaddr>']
        with open(fileaddr, 'r') as fp:
            for line in fp:
                print(decode(line))
