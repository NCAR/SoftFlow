from BaseHTTPServer import BaseHTTPRequestHandler
import os
import cgi
import logging
import uuid

curdir = os.path.dirname(os.path.realpath(__file__))
sep = '/'
TAB = 4

t_page = """<!DOCTYPE html>
%(html)s"""

t_html = """
<html>
    %(head)s
    %(body)s
</html>"""

t_head = """
<head>
    <title>%(title)s</title>
    <link rel="stylesheet" type="text/css" href="css/dspo.css">
    <script type="text/javascript" src="js/dspo.js" ></script>
        <script src="jquery.js" type="text/javascript"></script>
        <script src="jquery.easing.js" type="text/javascript"></script>
        <script src="jqueryFileTree.js" type="text/javascript"></script>
        <link href="jqueryFileTree.css" rel="stylesheet" type="text/css" media="screen" />
        <script type="text/javascript">
            $(document).ready( function() {
                $('#fileTreeDemo_1').fileTree({ root: '/', script: '/load' }, function(file) {
                    alert(file);
                });
            });
        </script>
</head>"""

t_body = """
<body>
    %(divmain)s
    %(divnav)s
    <img id="topleft" src="img/triangle-top-left.png" alt="Open side menu" height="50" width="50" onclick="openNav()">
    <a href="exit"><img id="topright" src="img/triangle-top-right.png" alt="Exit" height="50" width="50"></a>
</body>"""

t_divmain = """
<div id="main">
    %(content)s
    <div id="fileTreeDemo_1" class="demo"></div>
</div>"""

t_divnav = """
<div id="mySidenav" class="sidenav">
    <a href="javascript:void(0)" class="closebtn" onclick="closeNav()">&times;</a>
    %(menu)s
</div>"""

c_new = """
<div class="wrapper">
    <form action="/load">
      <input type="file" name="myfile">
      <input type="submit" value="Submit">
    </form>
</div>"""

def _indent(lines):
    return ' '*TAB + lines.replace('\n', '\n'+' '*TAB)

class DSPOPages(object):
    def __init__(self, sid):
        self.sid = sid
        self.lastpage = None
        self.jsondata = None

    def genc_new(self):
        return _indent(c_new)

    def genpage(self, path):
        return t_page%{'html': self.genhtml(path) }

    def genhtml(self, path):
        return t_html%{ 'head': self.genhead(path), 'body': self.genbody(path)}

    def genhead(self, path):
        return _indent(t_head%{ 'title': 'TITLE' })

    def genbody(self, path):
        return _indent(t_body%{'divmain': self.gendivmain(path), 'divnav': self.gendivnav(path)})

    def gendivmain(self, path):

        content = 'CONTENT'

        if path in [ '/', '/new' ]:
            content = self.genc_new()

        return _indent(t_divmain%{ 'content': content })

    def gendivnav(self, path):

        menuitems = [ \
            '<a href="/new">New</a>' \
        ]

        return _indent(t_divnav%{ 'menu': '\n'.join(menuitems) })

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
                            pass
                            #new session ?
                        else:
                            pass
                            #lost session => redirect
                    else:
                        #new session !
                        sid = str(uuid.uuid1())
                        gen = DSPOPages(sid)
                        self.session[sid] = gen
                        self.wfile.write(gen.genpage(path))
                else:
                    if 'sid' in params:
                        if params['sid'] in self.session:
                            self.wfile.write(self.session[params['sid']].genpage(path))
                        else:
                            pass
                            #lost session => redirect
                    else:
                        pass
                        #no session => redirect

        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)


    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write("<html><body><h1>POST is not supported!</h1></body></html>")
