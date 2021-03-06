#!/usr/bin/env python3

"""
This is a very simple web server that will listen to any incoming request and
log it to the console.

You can optionally specify a certificate file to use HTTPS.

You can also try to prompt for basic auth or NTLM auth. Currently, the --ntlm
flag will only tell you whether or not the client supports NTLM, as I haven't
implemented a full decoder yet.
Might be useful when doing pentests where Burp for some reason isn't an option,
or to track pingbacks Collaborator style.

Here is how you generate a certificate to use:
    openssl genrsa -out c.key 2048
    openssl req -new -x509 -days 3650 -key c.key -out c.crt
        \ -subj "/C=AU/ST=NSW/L=Sydney/O=IT/OU=IT/CN=*.somewhere.com"
    cat c.key c.crt > ssl.pem

(Or use my cert cloner here:
https://github.com/initstring/pentest/blob/master/web-tools/clone-ssl.py)

Then run this tool with the '--cert ssl.pem'

Enjoy!
"""

try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import sys
    import ssl
    import argparse
    import os
    import re
    import base64
except ImportError:
    print("\nError importing required modules... Are you using Python3?\n"
          "...you should be.\n")
    sys.exit(1)


if sys.version_info < (3, 0):
    print("\nSorry mate, you'll need to use Python 3+ on this one...\n")
    sys.exit(1)


GENERIC_HTML = 'This is a page, yay.'
NTLM_CHALLENGE = '1122334455667788'


class PC:
    """PC (Print Color)
    Used to generate some colorful, relevant, nicely formatted status messages.
    """
    green = '\033[92m'
    blue = '\033[94m'
    orange = '\033[93m'
    red = '\033[91m'
    endc = '\033[0m'
    ok_box = blue +    '[*] ' + endc
    err_box = red +    '[+] ' + endc
    req_box = green +  '[REQUEST FROM] ' + endc
    creds_box = red +  '[CREDS GIVEN]  ' + endc


def build_handler(args):
    """Build the class with the provided user arguments"""

    class HTTPClass(BaseHTTPRequestHandler):
        """
        This class will respond to any GET/POST/HEAD,
        logging details to the console.
        """
        protocol_version = 'HTTP/1.1'
        def generic_reply(self):
            """
            Just sends a simple 200 and the GENERIC_HTML defined above.
            If using optional basic auth, will prompt for credentials first
            """
            if args.basic:
                if 'Authorization' not in self.headers:
                    self.request_basic_auth()
                elif 'Basic ' in self.headers['Authorization']:
                    self.process_basic_auth()
            elif args.ntlm:
                if 'Authorization' not in self.headers:
                    self.request_ntlm_auth()
                elif 'NTLM ' in self.headers['Authorization']:
                    self.process_ntlm_auth()
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Connection', 'Close')
                self.end_headers()
                self.wfile.write(GENERIC_HTML.encode())

        def request_basic_auth(self):
            """
            Will prompt user for credentials using basic auth.
            """
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm=\"Auth\"')
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("Unauthorized.".encode())

        def process_basic_auth(self):
            """
            Decodes basic auth username and password and prints to console
            """
            basic, encoded = self.headers['Authorization'].split(" ")
            plaintext = base64.b64decode(encoded).decode()
            print(PC.creds_box + "HOST: {}, CREDS: {}"
                  .format(self.address_string(), plaintext))
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Connection', 'Close')
            self.end_headers()
            self.wfile.write(GENERIC_HTML.encode())

        def request_ntlm_auth(self):
            """
            Will prompt user for credentials using basic auth.
            """
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'NTLM')
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("Unauthorized.".encode())

        def process_ntlm_auth(self):
            """
            Decodes basic auth username and password and prints to console

            This function is under development and not complete.
            """
            ntlm_payload = self.headers['Authorization'].replace('NTLM ', '')
            ntlm_payload = base64.b64decode(ntlm_payload)
            challenge = ('TlRMTVNTUAACAAAADAAMADAAAAABAoEAASNFZ4mrze8AAAAAAAA'
                         'AAGIAYgA8AAAARABPAE0AQQBJAE4AAgAMAEQATwBNAEEASQBOAA'
                         'EADABTAEUAUgBWAEUAUgAEABQAZABvAG0AYQBpAG4ALgBjAG8Ab'
                         'QADACIAcwBlAHIAdgBlAHIALgBkAG8AbQBhAGkAbgAuAGMAbwBt'
                         'AAAAAAA=')
            if ntlm_payload[0:7] == b'NTLMSSP':
                if ntlm_payload[8:9] == b'\x01':
                    print(PC.ok_box + "beginning NTLMSSP conversation with {}"
                          .format(self.address_string()))
                    self.send_response(401)
                    self.send_header('WWW-Authenticate', 'NTLM {}'
                                     .format(challenge))
                    self.end_headers()
                    self.wfile.write("Unauthorized.".encode())
                else:
                    print(ntlm_payload)

        def do_GET(self):
            """Handles all GET requests"""
            self.generic_reply()

        def do_POST(self):
            """Handles all POST requests"""
            self.generic_reply()

        def do_HEAD(self):
            """Handles all HEAD requests"""
            self.generic_reply()

        def log_message(self, format, *args):
            """Handles all logging to the console."""
            print(PC.req_box + self.address_string())
            print(self.command + " " + self.path)
            print(self.headers)
            if self.command == 'POST':
                content_length = int(self.headers['Content-Length'])
                print(self.rfile.read(content_length).decode('utf-8'))

    return HTTPClass

def process_arguments():
    """Handle user-supplied arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument('interface', type=str, action='store',
                        help='Network interface to listen on.')
    parser.add_argument('--cert', '-c', type=str, action='store',
                        help='Certificate (pem) file to use.')
    parser.add_argument('-p', '--port', type=int, action='store',
                        help='Port. Default: 80 (or 443 if used with --cert)')
    parser.add_argument('-b', '--basic', default=False, action="store_true",
                        help="Prompt for basic auth")
    parser.add_argument('-n', '--ntlm', default=False, action="store_true",
                        help="Prompt for NTLM auth")

    args = parser.parse_args()

    if args.cert and not args.port:
        args.port = 443
    elif not args.port:
        args.port = 80

    return args

def get_ip(interface):
    """
    This function will attempt to automatically get the IP address of the
    provided interface.
    """
    try:
        local_ip = re.findall(r'inet (?:addr:)?(.*?) ',
                              os.popen('ifconfig ' + interface).read())[0]
    except Exception:
        print(PC.err_box + "Could not get network interface info."
              "Please check and try again.")
        sys.exit()
    return local_ip

def print_details(local_ip, local_port, basic_auth, cert_file):
    """Status message when launching the tool"""
    print("\n\n")
    print("########################################")
    print(PC.ok_box + "IP ADDRESS:           {}".format(local_ip))
    print(PC.ok_box + "PORT:                 {}".format(local_port))
    if basic_auth:
        print(PC.ok_box + "AUTH:                 Basic")
    if cert_file:
        print(PC.ok_box + "CERTFILE:             {}".format(cert_file))
    print("########################################\n\n")


def main():
    """Main application function"""
    args = process_arguments()
    local_ip = get_ip(args.interface)
    print_details(local_ip, args.port, args.basic, args.cert)
    HTTPSpy = build_handler(args)
    try:
        httpd = HTTPServer((local_ip, args.port), HTTPSpy)
    except PermissionError:
        print("\n" + PC.err_box + "You need root to bind to that port,"
              " try again with sudo.\n")
        sys.exit()
    if args.cert:
        httpd.socket = ssl.wrap_socket(httpd.socket, certfile=args.cert,
                                       server_side=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nThanks for playing, exiting now...\n")
        sys.exit()

if __name__ == "__main__":
    main()
