# UI for DSPO

import sys
import logging
import time
import multiprocessing
import webbrowser
import socket
import signal
import cv_webserver
from BaseHTTPServer import HTTPServer

db = {}

def launch_httpd(port):
    httpd = HTTPServer(('', port), cv_webserver.CVWebServer)
    httpd.session = {}
    try:
        httpd.serve_forever()
    except Exception as e:
        pass

def main():

    port = None

    for i in range(8000, 9000):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1',i))
        if result != 0:
            port = i
            break

    if port is None:
        return -1
    else:
        print '********************************************'
        print '* INFO: use "localhost:%d" to reconnect. *'%port
        print '********************************************'

        #multiprocessing.log_to_stderr(logging.INFO)

        # launch web server
        server = multiprocessing.Process(target=launch_httpd, args=(port, ))
        db['svrproc'] = server
        server.start()

        time.sleep(0.3)

        # launch web browser
        webbrowser.open_new('http://localhost:%d'%port)

        server.join()

        return 0

def signal_handler(signal, frame):
    db['svrproc'].terminate()
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    sys.exit(main())
