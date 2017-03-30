from BaseHTTPServer import BaseHTTPRequestHandler
import os
import urlparse
import urllib
import traceback
import logging
import uuid
import json
import ConfigParser

webserverdb = {}

curdir = os.path.dirname(os.path.realpath(__file__))
sep = '/'
TAB = 4

html_frame = """<!DOCTYPE html>
<html>
    <head>
        <title>KGen Coverage Viewer</title>
        <style>
            #code {
                text-align: left;
            }
        </style>
    </head>
    <body>
    %(body)s
    </body>
</html>"""

loaddata = """
<div id="main">
    <div id='content'>
        <center>
        <h1 >KGen Coverage File Viewer</h1>
        <h3><p><em>KGen Covereage Viewer</em> can show hot spots within source code.</h3>
        <hr width="50%%">
        <h3>Load KGen Coverage File</h3>
        <form id="data-form" method="GET" action="/data">
                <input id="input_load" type="text" name="datapath" value='/glade/u/home/youngsun/trepo/temp/kgen_workspace/tests_functional_coverage_test_basic/coverage.ini'>
                <input id="submit_load" type="submit" value='Submit'>
        </form>
        </center>
    </div>
</div>
"""

def page_index():
    return html_frame%{ 'body': loaddata }

def page_data(data):
    return html_frame%{ 'body': data }

def page_view(fileid):

    state = { 0: 'codeline', 1: 'visited', 2: 'notvisited' }
    curstate = 0

    blocks = webserverdb['blocks']
    visits = webserverdb['visits']
    linevisits = webserverdb['linevisits']
    filevisits = webserverdb['filevisits']
    visits_min = webserverdb['visits_min']
    visits_max = webserverdb['visits_max']
    visits_range = visits_max - visits_min
    path = webserverdb['files'][fileid]['path']
    lines = []
    with open(path) as f:
        lines.append('<table style="width:100%">')
        for idx, line in enumerate(f.read().split('\n')):

            encodedline = line.replace(' ', '&nbsp;')

            # state update
            if fileid in blocks and str(idx+1) in blocks[fileid]:
                row = '<tr><th id="code" style="background-color:white;">%s</th></tr>'%encodedline
                if blocks[fileid][str(idx+1)]:
                    curstate = 1
                else:
                    curstate = 2
            else:
                if curstate == 0:
                    row = '<tr><th id="code" style="background-color:white;">%s</th></tr>'%encodedline
                elif curstate in (1, 2):
                    lline = line.strip().lower()
                    if any( lline.startswith(key) for key in ('if', 'else', 'end') ):
                        row = '<tr><th id="code" style="background-color:white;">%s</th></tr>'%encodedline
                        curstate = 0
                    elif curstate == 1:
                        color = int( (linevisits[fileid][str(idx)] - visits_min) * 1.0 / visits_range * 155.0 + 100.0 )
                        tooltip = str(linevisits[fileid][str(idx)])
                        #tooltip = '%s, mpi: %s, openmp: %s'%(str(linevisits[fileid][str(idx)]), str(visits[fileid][str(idx)]['mpivisits']), \
                        #    str(visits[fileid][str(idx)]['ompvisits']))
                        #tooltip = '%s, mpi: %s, openmp: %s'%(str(linevisits[fileid][str(idx)]), str(visits[fileid][str(idx)]['mpivisits']), \
                        #    str(visits[fileid][str(idx)]['ompvisits']))
                        row = '<tr><th id="code" title="%s" style="background-color:rgb(%d,0,0);">%s</th></tr>'%(tooltip, color, encodedline)
                    elif curstate == 2:
                        row = '<tr><th id="code" title="No visit" style="background-color:grey;">%s</th></tr>'%encodedline

            lines.append(row)
        lines.append('</table>')
    #return '<br>\n'.join(lines).replace(' ', '&nbsp;')
    return html_frame%{ 'body': '\n'.join(lines) }

class CVWebServer(BaseHTTPRequestHandler):

    def _set_headers(self, mimetype='text/html'):
        self.send_response(200)
        self.send_header('Content-type', mimetype)
        self.end_headers()

    def do_GET(self):
        try:
            query = self.path.split("?")
            path = query[0]
            params = {}
            if len(query) > 1:
                params = dict(urlparse.parse_qsl(query[1], True, True))

            sendReply = False
            if path=='/favicon.ico':
                return
            if path.endswith(".jpg"):
                mimetype='image/jpg'
                sendReply = True
            if path.endswith(".gif"):
                mimetype='image/gif'
                sendReply = True
            if path.endswith(".png"):
                mimetype='image/png'
                sendReply = True
            if path.endswith(".js"):
                mimetype='application/javascript'
                sendReply = True
            if path.endswith(".css"):
                mimetype='text/css'
                sendReply = True
            if path.endswith(".json"):
                mimetype='application/json'
                sendReply = True

            if sendReply == True:
                with open(curdir + sep + self.path) as f:
                    self._set_headers(mimetype)
                    self.wfile.write(f.read())
            else:

                self._set_headers()
                if path == '/':
                    self.wfile.write(page_index())
                elif path == '/data':
                    datapath = urllib.unquote(params['datapath']).decode('utf8')
                    config = ConfigParser.RawConfigParser()
                    config.read(datapath)
                    webserverdb['coverage_ini'] = config
                    outlines = []

                    # title
                    outlines.append('<h1>Coverage Data</h1>')

                    # summary
                    outlines.append('<h2>SUMMARY</h2>')
                    for opt in config.options('summary'):
                        outlines.append('%s = %s'%(opt, config.get('summary', opt)))

                    # file
                    files = {}
                    usedfiles = tuple( fid.strip() for fid in config.get('file', 'used_files').split(','))
                    for fid in usedfiles:
                        if fid not in files:
                            files[fid] = {}
                            files[fid]['used'] = True

                    outlines.append('<h2>FILE</h2>')
                    for opt in config.options('file'):
                        if opt.isdigit():
                            path = config.get('file', opt)
                            if opt in files:
                                files[opt]['path'] = path
                                outlines.append('<a href="/view?fileid=%s">%s</a>'%(opt, os.path.basename(path)))
                            else:
                                files[opt] = {}
                                files[opt]['path'] = path
                                files[opt]['used'] = False
                                outlines.append(os.path.basename(path))
                    webserverdb['files'] = files

                    # block
                    blocks = {}
                    usedpairs = tuple( pair.strip().split(':') for pair in config.get('block', 'used_blocks').split(','))
                    for fid, lnum in usedpairs:
                        if fid not in blocks:
                            blocks[fid] = {}
                        if lnum not in blocks[fid]:
                            blocks[fid][lnum] = True
                    for opt in config.options('block'):
                        if opt.isdigit():
                            if opt not in blocks:
                                blocks[opt] = {}
                            lnums = tuple( lnum.strip() for lnum in config.get('block', opt).split(',') )
                            for lnum in lnums:
                                if lnum not in blocks[opt]:
                                    blocks[opt][lnum] = False
                    webserverdb['blocks'] = blocks

                    # visits
                    visits = {} # fileid, linenum, { 'totalvisits': N, 'mpivisits': { mpi: N }, 'ompvisits': { omp: N } }
                    linevisits = {}
                    filevisits = {}
                    for opt in config.options('invoke'):
                        mpi, omp, invoke = opt.split()
                        for visits_triple in config.get('invoke', opt).split(','):
                            fid, lnum, nvisits = visits_triple.strip().split(':')

                            if fid not in visits:
                                visits[fid] = {}
                                linevisits[fid] = {}
                            if lnum not in visits[fid]:
                                visits[fid][lnum] = {}
                                linevisits[fid][lnum] = 0

                            if 'mpivisits' not in visits[fid][lnum]:
                                visits[fid][lnum]['mpivisits'] = {}
                            if mpi not in visits[fid][lnum]['mpivisits']:
                                visits[fid][lnum]['mpivisits'][mpi] = int(nvisits)
                            else:
                                visits[fid][lnum]['mpivisits'][mpi] += int(nvisits)

                            if 'ompvisits' not in visits[fid][lnum]:
                                visits[fid][lnum]['ompvisits'] = {}
                            if omp not in visits[fid][lnum]['ompvisits']:
                                visits[fid][lnum]['ompvisits'][omp] = int(nvisits)
                            else:
                                visits[fid][lnum]['ompvisits'][omp] += int(nvisits)

                    visits_min = 100000000000000000000000
                    visits_max = 0
                    for fileid, linenums in visits.items():
                        for lnum, visits in linenums.items():
                            for visit in visits['mpivisits'].values():
                                linevisits[fileid][lnum] += visit
                            visits_min = min(visits_min, linevisits[fileid][lnum])
                            visits_max = max(visits_max, linevisits[fileid][lnum])
                        filevisits[fileid] = sum(linevisits[fileid].values())

                    webserverdb['visits'] = visits
                    webserverdb['linevisits'] = linevisits
                    webserverdb['filevisits'] = filevisits
                    webserverdb['visits_min'] = visits_min
                    webserverdb['visits_max'] = visits_max

                    self.wfile.write(page_data('<br>\n'.join(outlines)))

                elif path == '/view':
                    self.wfile.write(page_view(params['fileid']))
 
                else:
                    self.send_error(404,'File Not Found: %s' % self.path)
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

        except Exception as e:
            self.send_error(520, traceback.format_exc().replace('\n', '<br>\n').replace(' ', '&nbsp;'))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write("<html><body><h1>POST is not supported!</h1></body></html>")
