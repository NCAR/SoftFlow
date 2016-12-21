from BaseHTTPServer import BaseHTTPRequestHandler
import os
import cgi
import logging

curdir = os.path.dirname(os.path.realpath(__file__))
sep = '/'

page = """
<!DOCTYPE html>
<html>
    <head>
        <title>Page Title</title>
        <link rel="stylesheet" type="text/css" href="css/dspo.css">
        <script type="text/javascript" src="js/dspo.js" ></script>
    </head>

    <body>
        <!-- Add all page content inside this div if you want the side nav 
            to push page content to the right (not used if you only want 
            the sidenav to sit on top of the page -->
        <div id="main">
%(content)s
        </div>


        <div id="mySidenav" class="sidenav">
          <a href="javascript:void(0)" class="closebtn" onclick="closeNav()">&times;</a>
%(menu)s
        </div>

        <img id="topleft" src="img/triangle-top-left.png" alt="Open side menu" height="50" width="50" onclick="openNav()">
        <a href="exit"><img id="topright" src="img/triangle-top-right.png" alt="Exit" height="50" width="50"></a>

    </body>
</html>
"""
"""
          <a href="#">About</a>
          <a href="#">Services</a>
          <a href="#">Clients</a>
          <a href="#">Contact</a>
"""

class DSPOWebServer(BaseHTTPRequestHandler):

    def __init__(self, *args):
        self.session = {}
        BaseHTTPRequestHandler.__init__(self, *args)

    def _set_headers(self, mimetype='text/html'):
        self.send_response(200)
        self.send_header('Content-type', mimetype)
        self.end_headers()

    def do_GET(self):
        try:
            sendReply = False
            if self.path=='/favicon.ico':
                return
            if self.path.endswith(".jpg"):
                mimetype='image/jpg'
                sendReply = True
            if self.path.endswith(".gif"):
                mimetype='image/gif'
                sendReply = True
            if self.path.endswith(".png"):
                mimetype='image/png'
                sendReply = True
            if self.path.endswith(".js"):
                mimetype='application/javascript'
                sendReply = True
            if self.path.endswith(".css"):
                mimetype='text/css'
                sendReply = True

            if sendReply == True:
                f = open(curdir + sep + self.path) 
                self._set_headers(mimetype)
                self.wfile.write(f.read())
                f.close()
            else:
                query = self.path.split("?")
                path = query[0]
                params = {}
                if len(query) > 1:
                    params = cgi.parse_qs(query[1], True, True)

                #logging.warning('%s %s %s'%(query, path, str(params)))

                self._set_headers()

                if path == '/':
                    if 'sid' in params:
                        if params['sid'] in self.session:
                            new session ?
                        else:
                            lost session => redirect
                    else:
                        new session !
                        #self.wfile.write(page)

                else:
                    if 'sid' in params:
                        if params['sid'] in self.session:
                            self.wfile.write(self.session[params['sid']].genpage(path))
                        else:
                            lost session => redirect
                    else:
                        no session => redirect

        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)


    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write("<html><body><h1>POST is not supported!</h1></body></html>")
