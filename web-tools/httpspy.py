#!/usr/bin/env python3

"""
This is a very simple web server that will listen to any incoming request and log it to the console.
You can optionally specific a certificate file to use HTTPS.
Might be useful when doing pentests where Burp for some reason isn't an option.

Here is how you generate a certificate to use:
    openssl genrsa -out c.key 2048
    openssl req -new -x509 -days 3650 -key c.key -out c.crt -subj "/C=AU/ST=NSW/L=Sydney/O=IT/OU=IT/CN=*.somewhere.com"
    cat c.key c.crt > ssl.pem

Then run this tool with the '--cert ssl.pem'

Enjoy!
"""

import sys
if sys.version_info < (3, 0):
    print("\nSorry mate, you'll need to use Python 3+ on this one...\n")
    sys.exit(1)

from http.server import HTTPServer,BaseHTTPRequestHandler
import ssl,argparse,os,re;
#############################           Global Variable Declarations           #############################

class bcolors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
okBox = bcolors.BLUE +      '[*] ' + bcolors.ENDC
reqBox = bcolors.GREEN +    '[REQUEST]     ' + bcolors.ENDC

parser = argparse.ArgumentParser()
parser.add_argument('interface', type=str, help='Network interface to listen on.', action='store')
parser.add_argument('--cert', '-c', type=str, help='Certificate (pem) file to use.', action='store')
parser.add_argument('-p', '--port', type=int, help='Port for HTTP server. Defaults to 80 or 443 if a \
                    cert file is specified', action='store')
args = parser.parse_args()

interface = args.interface
localPort = args.port or False

if args.cert:
    certFile = args.cert
    if not localPort:
        localPort = 443
else:
    certFile = False
    if not localPort:
        localPort = 80


genericHTML = "This is a page, yay."

#############################         End Global Variable Declarations          #############################

class HTTPSpy(BaseHTTPRequestHandler):
    """
    This class will respond to any GET/POST/HEAD, logging the details to the console.
    """
    def generic_reply(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(genericHTML.encode())

    def do_GET(self):
        self.generic_reply()

    def do_POST(self):
        self.generic_reply()

    def do_HEAD(self):
        self.generic_reply()
    
    def log_message(self, format, *args):    
        print(reqBox + self.address_string())
        print(self.command + " " + self.path)
        print(self.headers)
        if self.command == 'POST':
            contentLength = int(self.headers['Content-Length'])
            print(self.rfile.read(contentLength).decode('utf-8'))


        
def get_ip(interface):
    """
    This function will attempt to automatically get the IP address of the provided interface.
    """
    try:
        localIp = re.findall(r'inet (?:addr:)?(.*?) ', os.popen('ifconfig ' + interface).read())[0]
    except Exception:
        print(warnBox + "Could not get network interface info. Please check and try again.")
        sys.exit()
    return localIp

def print_details(localIp, localPort):
    print("\n\n")
    print("########################################")
    print(okBox + "IP ADDRESS:           {}".format(localIp))
    print(okBox + "PORT:                 {}".format(localPort))
    print("########################################\n\n")


def main():
    localIp = get_ip(interface)                         # Obtain IP address of target interface
    print_details(localIp, localPort)                   # Print a nice status box
    httpd = HTTPServer((localIp, localPort), HTTPSpy)   # Start the HTTP server
    if certFile:                                        # If using a certificate, wrap in SSL
        httpd.socket = ssl.wrap_socket(httpd.socket, certfile=certFile, server_side=True)
    httpd.serve_forever()                               # Start the webserver

if __name__ == "__main__":
    main()
