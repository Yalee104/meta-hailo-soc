#!/usr/bin/env python3
import sys
import struct
import os

def main():
    # Usage: <exec> <key cert> <content cert> <output>
    key_cert_size = os.path.getsize(sys.argv[1])
    content_cert_size = os.path.getsize(sys.argv[2])
    key_cert_data = open(sys.argv[1], 'rb').read()
    content_cert_data = open(sys.argv[2], 'rb').read()
    cert_chain_binary = open(sys.argv[3], 'wb')
    cert_chain_binary.write(struct.pack('<II', key_cert_size, content_cert_size))
    cert_chain_binary.write(key_cert_data)
    cert_chain_binary.write(content_cert_data)

if __name__ == '__main__':
    main()
