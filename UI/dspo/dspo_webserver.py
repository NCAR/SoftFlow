from BaseHTTPServer import BaseHTTPRequestHandler
import os
import sys
import urlparse
import urllib
import logging
import uuid
import json

curdir = os.path.dirname(os.path.realpath(__file__))
sep = '/'
TAB = 4


curdir = os.path.dirname(os.path.realpath(__file__))
sep = '/'
TAB = 4

index_page = """<!DOCTYPE html>
<html>
    <head>
        <title>TITLE</title>
        <link rel="stylesheet" type="text/css" href="css/dspo.css">
        <script type="text/javascript" src="js/dspo.js" ></script>
    </head>
    <body>
        <div id="main">
            <div id='content'>
                <h1 >Learn From Controlled Experiments</h1>
                <h3><p><em>Within this tool</em>, complex software performance data can be easily explored and analyzed.</h3>
                <hr width="50%%">
                <br><br>%(msg)s<br>
                <h3>Load new experiment data</h3>
                <form id="welcome-form" method="GET" action="/data">
                        <input type="hidden" name="sid" value='%(sid)s'>
                        <input id="input_load" type="text" name="datapath" value='/home/youngsung/repos/github/SoftFlow/UI/dspo/result.json'>
                        <input id="submit_load" type="submit" value='Submit'>
                </form>
            </div>
        </div>
    </body>
</html>"""

data_page = """<!DOCTYPE html>
<html>
<head>

    <title>Simple Layout Demo</title>

    <meta http-equiv="Content-Type" content="text/html" charset="UTF-8" />
    <link type="text/css" rel="stylesheet" href="css/layout-default-latest.css" />
    <link type="text/css" rel="stylesheet" href="css/jquery.bonsai.css" />

    <script type="text/javascript" src="js/jquery-2.2.4.js"></script>
    <script type="text/javascript" src="js/jquery-ui.js"></script>
    <script type="text/javascript" src="js/jquery.layout-latest.js"></script>
    <script src='js/jquery.bonsai.js'></script>
<!--    <script src='js/jquery.json-list.js'></script> -->
    <script src='js/jquery.qubit.js'></script>
    <script type="text/javascript">
    // set EVERY 'state' here so will undo ALL layout changes
    // used by the 'Reset State' button: myLayout.loadState( stateResetSettings )
    var stateResetSettings = {
        north__size:        "auto"
    ,   north__initClosed:  false
    ,   north__initHidden:  false
    ,   south__size:        "auto"
    ,   south__initClosed:  false
    ,   south__initHidden:  false
    ,   west__size:         200
    ,   west__initClosed:   false
    ,   west__initHidden:   false
    ,   east__size:         300
    ,   east__initClosed:   false
    ,   east__initHidden:   false
    };

    var myLayout;

    $(document).ready(function () {

        // this layout could be created with NO OPTIONS - but showing some here just as a sample...
        // myLayout = $('body').layout(); -- syntax with No Options

        myLayout = $('body').layout({

        //  reference only - these options are NOT required because 'true' is the default
            closable:                   true    // pane can open & close
        ,   resizable:                  true    // when open, pane can be resized
        ,   slidable:                   true    // when closed, pane can 'slide' open over other panes - closes on mouse-out
        ,   livePaneResizing:           true

        //  some resizing/toggling settings
        ,   north__slidable:            false   // OVERRIDE the pane-default of 'slidable=true'
        ,   north__togglerLength_closed: '100%%' // toggle-button is full-width of resizer-bar
        ,   north__spacing_closed:      20      // big resizer-bar when open (zero height)
        ,   south__resizable:           true   // OVERRIDE the pane-default of 'resizable=true'
        ,   south__spacing_open:        5       // no resizer-bar when open (zero height)
        ,   south__spacing_closed:      20      // big resizer-bar when open (zero height)

        //  some pane-size settings
        ,   west__minSize:              100
        ,   east__size:                 300
        ,   east__minSize:              200
        ,   east__maxSize:              .5 // 50%% of layout width
        ,   center__minWidth:           100

        //  some pane animation settings
        ,   west__animatePaneSizing:    false
        ,   west__fxSpeed_size:         "fast"  // 'fast' animation when resizing west-pane
        ,   west__fxSpeed_open:         1000    // 1-second animation when opening west-pane
        ,   west__fxSettings_open:      { easing: "easeOutBounce" } // 'bounce' effect when opening
        ,   west__fxName_close:         "none"  // NO animation when closing west-pane

        //  enable showOverflow on west-pane so CSS popups will overlap north pane
        ,   west__showOverflowOnHover:  false

        //  enable state management
        ,   stateManagement__enabled:   true // automatic cookie load & save enabled by default

        ,   showDebugMessages:          true // log and/or display messages from debugging & testing code
        });
    });

    jQuery(function() {
        $('.datatree').bonsai({
            expandAll: true,
            checkboxes: true, // depends on jquery.qubit plugin
            handleDuplicateCheckboxes: true // optional
        });
    });

    </script>


</head>
<body>

<div class="ui-layout-north">
    <center><h1 >Data Explorer</h1></center>
</div>

<div class="ui-layout-west">
    %(westtree)s
</div>

<div class="ui-layout-south">
    SOUTH
</div>

<div class="ui-layout-east">
    %(easttree)s
</div>

<div class="ui-layout-center">
    CENTER
</div>

</body>
</html>
"""

c_msg = '<p style="padding: 10px; color: red; border: black 2px solid">%s</p>'

def _indent(lines, width=TAB):
    return ' '*width + lines.replace('\n', '\n'+' '*width)

class DSPOPages(object):
    def __init__(self):
        self.sid = str(uuid.uuid1())
        self.lastpage = None
        self.jsondata = None

    def genindex(self, msg='' ):
        return index_page%{'msg': msg, 'sid': self.sid}

    def gendata(self, data ):
        def checkjson(indata):
            if not isinstance(indata, dict): raise Exception("Not a dictionary")
            if len(indata) == 0: raise Exception("Blank data")

            for jid, content in indata.items():
                if not isinstance(content, dict): raise Exception("%s is not a dictionary"%str(jid))
                if len(content) == 0: raise Exception("%s has no data"%str(jid))
                if not content.has_key('cgroup'): raise Exception("%s has no cgroup"%str(jid))
                if not content.has_key('egroup'): raise Exception("%s has no egroup"%str(jid))
                if len(content['cgroup']) == 0: raise Exception("%s cgroup has no data"%str(jid))
                if len(content['egroup']) == 0: raise Exception("%s egroup has no data"%str(jid))

        def gentree(indata, itemid=0, depth=0):
            outstr = ''
            if isinstance(indata, dict):
                if depth == 0:
                    outstr += '<ol class="datatree">\n'
                else:
                    outstr += ' '*depth + '\n<ol>\n'
                for key, value in indata.items():
                    itemid += 1
                    outstr += '<li><input type="checkbox" value="%d" checked />%s:\n%s %s</li>'%\
                        (itemid, key, ' '*depth, gentree(value, itemid, depth+TAB))
                outstr += ' '*depth + '</ol>\n'
            elif isinstance(indata, (list, tuple)):
                if any(isinstance(subdata, (dict, list, tuple)) for subdata in indata):
                    outstr += ' '*depth + '<ol>\n'
                    if isinstance(indata, (dict, list, tuple)):
                        for subdata in indata:
                            itemid += 1
                            outstr += gentree(subdata, itemid, depth+TAB)
                    else:
                        outstr += '%s\n'%str(indata)
                    outstr += ' '*depth + '</ol>\n'
                else:
                    outstr += '%s\n'%str(indata)
            else:
                outstr += '%s\n'%str(indata)
            return outstr
        try:
            checkjson(data)
            west = {}
            east = {}
            common = {}
            attr = {}
            for jid, content in data.items():
                attr[jid] = content.get('__attr__', {})
                common[jid] = content.get('common', {})
                west[jid] = content.get('cgroup', {})
                east[jid] = content.get('egroup', {})
            # merge common to west and east
            westtree = gentree(west)
            easttree = gentree(east)
        except Exception as e:
            tree = 'JOSN file check error: %s'%str(e)
        return _indent(data_page%{'sid': self.sid, 'westtree': westtree, 'easttree': easttree})

    def genpage(self, path, params):

        page = 'CONTENT'

        if path == '/':
            msg = ''
            sidmsg = params.get('sid', '')
            if sidmsg == 'notexist':
                msg = c_msg%"Session does not exist. Please reload experiment data."
            elif sidmsg == 'notfound':
                msg = c_msg%"Session could not be found. Please reload experiment data."
            page = self.genindex(msg=msg)
        elif path == '/data':
            # data file
            try:
                datapath = urllib.unquote(params['datapath']).decode('utf8')
                logging.warning(datapath)
                data = {}
                with open(datapath) as jfile:
                    data = json.load(jfile)
                page = self.gendata(data)
            except Exception as e:
                msg = c_msg%'"%s<br>%s" could not be found. Please check file path.'%(str(e), datapath)
                page = self.genindex(msg=msg)
            # generate summary page
        else:
            logging.warning("%s is not supported yet."%path)

        return page

class DSPOWebServer(BaseHTTPRequestHandler):

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
                f = open(curdir + sep + self.path)
                self._set_headers(mimetype)
                self.wfile.write(f.read())
                f.close()
            else:

                #logging.warning('%s %s %s'%(query, path, str(params)))

                self._set_headers()

                newsession = False

                if 'sid' in params:
                    if params['sid'] in self.server.session:
                        self.wfile.write(self.server.session[params['sid']].genpage(path, params))
                    else:
                        path = '/'
                        params['sid'] = 'notfound'
                        newsession = True
                else:
                    newsession = True
                    if path != '/':
                        path = '/'
                        params['sid'] = 'notexist'

                if newsession:
                    gen = DSPOPages()
                    self.server.session[gen.sid] = gen
                    self.wfile.write(gen.genpage(path, params))

        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)


    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write("<html><body><h1>POST is not supported!</h1></body></html>")
