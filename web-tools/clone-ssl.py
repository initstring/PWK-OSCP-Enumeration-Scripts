#!/usr/bin/env python3
import argparse,OpenSSL,ssl;

"""
This script allows you to create a TLS keypair similar to a target.
May be useful for things like mobile app pentesting.
In the future, should probably extend to create a chain similar to the target.
Enjoy!

Thanks to this thread:
https://stackoverflow.com/questions/7689941/how-can-i-retrieve-the-tls-ssl-peer-certificate-of-a-remote-host-using-python
"""

#############################           Global Variable Declarations           #############################

parser = argparse.ArgumentParser()
parser.add_argument('domain', type=str, help='Domain name to grab cert from (i.e. google.com)', action='store')
parser.add_argument('--port', '-p', type=int, default=443, help='Target port (default 443)', action='store')
args = parser.parse_args()

targetDomain = args.domain
targetPort = args.port

#############################         End Global Variable Declarations          #############################


def get_cert(targetDomain, targetPort):
    try:
        pemFile = ssl.get_server_certificate((targetDomain, targetPort))
        print("[+] Got the certificate...")
        return pemFile
    except:
        print("[!] Sorry, error getting certificate from {} on port {}.".format(targetDomain, targetPort))

def parse_cert(pemFile):
    certObject = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, pemFile)
    certSubject = str(certObject.get_subject()).split("'")[1]
    certSerial = str(certObject.get_serial_number())
    print("[+] Parsed the certificate")
    return(certSubject, certSerial)

def make_cert(subj, ser):
    c1 = 'openssl genrsa -out tls.key 2048'
    c2 = 'openssl req -new -x509 -days 3650 -set_serial {} -key tls.key -out tls.crt -subj "{}"'.format(ser, subj)
    print("[+] Run the following commands to make your keypair:")
    print(c1 + "\n" + c2)

def main():
    pemFile = get_cert(targetDomain, targetPort)
    certSubject,certSerial = parse_cert(pemFile)
    make_cert(certSubject, certSerial)


if __name__ == "__main__":
    main()
