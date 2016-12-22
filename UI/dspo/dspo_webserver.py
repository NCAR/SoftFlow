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
                        <input id="input_load" type="text" name="datapath" value='/Users/youngsun/trepo/temp/result.json'>
                        <input id="submit_load" type="submit" value='Submit'>
                </form>
            </div> 
        </div>
    </body>
</html>"""

data_page = """<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>

    <title>Simple Layout Demo</title>

    <link type="text/css" rel="stylesheet" href="css/layout-default-latest.css" />

    <style type="text/css">

    p {
        font-size:      1em;
        margin:         1ex 0;
    }
    p.buttons {
        text-align:     center;
        line-height:    2.5em;
    }
    button {
        line-height:    normal;
    }
    .hidden {
        display:        none;
    }

    /*
     *  Rules for simulated drop-down/pop-up lists
     */
    ul {
        /* rules common to BOTH inner and outer UL */
        z-index:    100000;
        margin:     1ex 0;
        padding:    0;
        list-style: none;
        cursor:     pointer;
        border:     1px solid Black;
        /* rules for outer UL only */
        width:      15ex;
        position:   relative;
    }
    ul li {
        background-color: #EEE;
        padding: 0.15em 1em 0.3em 5px;
    }
    ul ul {
        display:    none;
        position:   absolute;
        width:      100%%;
        left:       -1px;
        /* Pop-Up */
        bottom:     0;
        margin:     0;
        margin-bottom: 1.55em;
    }
    .ui-layout-north ul ul {
        /* Drop-Down */
        bottom:     auto;
        margin:     0;
        margin-top: 1.45em;
    }
    ul ul li        { padding: 3px 1em 3px 5px; }
    ul ul li:hover  { background-color: #FF9; }
    ul li:hover ul  { display:  block; background-color: #EEE; }

    </style>

    <!-- LAYOUT v 1.3.0 -->
    <script type="text/javascript" src="js/jquery-latest.js"></script>
    <script type="text/javascript" src="js/jquery-ui-latest.js"></script>
    <script type="text/javascript" src="js/jquery.layout-1.3.0.rc30.80.js"></script>

    <script type="text/javascript" src="js/debug.js"></script>

    <script type="text/javascript">

    function toggleLiveResizing () {
        $.each( $.layout.config.borderPanes, function (i, pane) {
            var o = myLayout.options[ pane ];
            o.livePaneResizing = !o.livePaneResizing;
        });
    };
    
    function toggleStateManagement ( skipAlert, mode ) {
        if (!$.layout.plugins.stateManagement) return;

        var options = myLayout.options.stateManagement
        ,   enabled = options.enabled // current setting
        ;
        if ($.type( mode ) === "boolean") {
            if (enabled === mode) return; // already correct
            enabled = options.enabled = mode
        }
        else
            enabled = options.enabled = !enabled; // toggle option

        if (!enabled) { // if disabling state management...
            myLayout.deleteCookie(); // ...clear cookie so will NOT be found on next refresh
            if (!skipAlert)
                alert( 'This layout will reload as the options specify when the page is refreshed.' );
        }
        else if (!skipAlert)
            alert( 'This layout will save & restore its last state when the page is refreshed.' );

        // update text on button
        var $Btn = $('#btnToggleState'), text = $Btn.html();
        if (enabled)
            $Btn.html( text.replace(/Enable/i, "Disable") );
        else
            $Btn.html( text.replace(/Disable/i, "Enable") );
    };

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
        ,   south__spacing_open:        10       // no resizer-bar when open (zero height)
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
        ,   west__showOverflowOnHover:  true

        //  enable state management
        ,   stateManagement__enabled:   true // automatic cookie load & save enabled by default

        ,   showDebugMessages:          true // log and/or display messages from debugging & testing code
        });

        // if there is no state-cookie, then DISABLE state management initially
        var cookieExists = !$.isEmptyObject( myLayout.readCookie() );
        if (!cookieExists) toggleStateManagement( true, false );

        myLayout
            // add event to the 'Close' button in the East pane dynamically...
            .bindButton('#btnCloseEast', 'close', 'east')
    
            // add event to the 'Toggle South' buttons in Center AND South panes dynamically...
            .bindButton('.south-toggler', 'toggle', 'south')
            
            // add MULTIPLE events to the 'Open All Panes' button in the Center pane dynamically...
            .bindButton('#openAllPanes', 'open', 'north')
            .bindButton('#openAllPanes', 'open', 'south')
            .bindButton('#openAllPanes', 'open', 'west')
            .bindButton('#openAllPanes', 'open', 'east')

            // add MULTIPLE events to the 'Close All Panes' button in the Center pane dynamically...
            .bindButton('#closeAllPanes', 'close', 'north')
            .bindButton('#closeAllPanes', 'close', 'south')
            .bindButton('#closeAllPanes', 'close', 'west')
            .bindButton('#closeAllPanes', 'close', 'east')

            // add MULTIPLE events to the 'Toggle All Panes' button in the Center pane dynamically...
            .bindButton('#toggleAllPanes', 'toggle', 'north')
            .bindButton('#toggleAllPanes', 'toggle', 'south')
            .bindButton('#toggleAllPanes', 'toggle', 'west')
            .bindButton('#toggleAllPanes', 'toggle', 'east')
        ;


        /*
         *  DISABLE TEXT-SELECTION WHEN DRAGGING (or even _trying_ to drag!)
         *  this functionality will be included in RC30.80
         */
        $.layout.disableTextSelection = function(){
            var $d  = $(document)
            ,   s   = 'textSelectionDisabled'
            ,   x   = 'textSelectionInitialized'
            ;
            if ($.fn.disableSelection) {
                if (!$d.data(x)) // document hasn't been initialized yet
                    $d.on('mouseup', $.layout.enableTextSelection ).data(x, true);
                if (!$d.data(s))
                    $d.disableSelection().data(s, true);
            }
            //console.log('$.layout.disableTextSelection');
        };
        $.layout.enableTextSelection = function(){
            var $d  = $(document)
            ,   s   = 'textSelectionDisabled';
            if ($.fn.enableSelection && $d.data(s))
                $d.enableSelection().data(s, false);
            //console.log('$.layout.enableTextSelection');
        };
        $(".ui-layout-resizer")
            .disableSelection() // affects only the resizer element
            .on('mousedown', $.layout.disableTextSelection ); // affects entire document

    });
    </script>


</head>
<body>

<!-- manually attach allowOverflow method to pane -->
<div class="ui-layout-north" onmouseover="myLayout.allowOverflow('north')" onmouseout="myLayout.resetOverflow(this)">
    This is the north pane, closable, slidable and resizable

    <ul>
        <li>
            <ul>
                <li>one</li>
                <li>two</li>
                <li>three</li>
                <li>four</li>
                <li>five</li>
            </ul>
            Drop-Down <!-- put this below so IE and FF render the same! -->
        </li>
    </ul>

</div>

<!-- allowOverflow auto-attached by option: west__showOverflowOnHover = true -->
<div class="ui-layout-west">
    This is the west pane, closable, slidable and resizable
<button onclick="debugData(myLayout.options.west)">West Options</button>
    <ul>
        <li>
            <ul>
                <li>one</li>
                <li>two</li>
                <li>three</li>
                <li>four</li>
                <li>five</li>
            </ul>
            Pop-Up <!-- put this below so IE and FF render the same! -->
        </li>
    </ul>

    <p><button onclick="myLayout.close('west')">Close Me</button></p>

</div>

<div class="ui-layout-south">
    This is the south pane, closable, slidable and resizable &nbsp;

    <!-- this button has its event added dynamically in document.ready -->
    <button class="south-toggler">Toggle This Pane</button>
</div>

<div class="ui-layout-east">
    This is the east pane, closable, slidable and resizable

    <!-- attach allowOverflow method to this specific element -->
    <ul onmouseover="myLayout.allowOverflow(this)" onmouseout="myLayout.resetOverflow('east')">
        <li>
            <ul>
                <li>one</li>
                <li>two</li>
                <li>three</li>
                <li>four</li>
                <li>five</li>
            </ul>
            Pop-Up <!-- put this below so IE and FF render the same! -->
        </li>
    </ul>

    <!-- this button has its event added dynamically in document.ready -->
    <p><button id="btnCloseEast">Close Me</button></p>

    <p><select>
        <option value="19">Picklist Test</option>
        <option value="17">tropical storm</option>
        <option value="18">hurricane</option>
        <option value="19">severe thunderstorms</option>
        <option value="20">thunderstorms</option>
        <option value="21">mixed rain and snow</option>
        <option value="22">mixed rain and sleet</option>
        <option value="23">mixed snow and sleet</option>
        <option value="24">freezing drizzle</option>
        <option value="25">drizzle</option>
        <option value="26">freezing rain</option>
        <option value="27">showers</option>
        <option value="28">showers</option>
        <option value="29">snow flurries</option>
        <option value="30">light snow showers</option>
        <option value="31">blowing snow</option>
        <option value="32">snow</option>
        <option value="33">hail</option>
        <option value="34">sleet</option>
        <option value="35">dust</option>
        <option value="36">foggy</option>
        <option value="37">haze</option>
        <option value="38">smoky</option>
        <option value="39">blustery</option>
        <option value="40">windy</option>
        <option value="41">cold</option>
        <option value="42">cloudy</option>
        <option value="43">mostly cloudy (night)</option>
        <option value="44">mostly cloudy (day)</option>
        <option value="45">partly cloudy (night)</option>
        <option value="46">partly cloudy (day)</option>
        <option value="47">clear (night)</option>
        <option value="48">sunny</option>
        <option value="49">fair (night)</option>
        <option value="50">fair (day)</option>
        <option value="51">mixed rain and hail</option>
        <option value="52">hot</option>
        <option value="53">isolated thunderstorms</option>
        <option value="54">scattered thunderstorms</option>
        <option value="55">scattered thunderstorms</option>
        <option value="56">scattered showers</option>
        <option value="57">heavy snow</option>
        <option value="58">scattered snow showers</option>
        <option value="59">heavy snow</option>
        <option value="60">partly cloudy</option>
        <option value="61">thundershowers</option>
        <option value="62">snow showers</option>
        <option value="63">isolated thundershowers</option>
    </select></p>

    <p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p>
    <p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p>
    <p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p>
    <p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p>
</div>

<div class="ui-layout-center">
    This CENTER pane auto-sizes to fit the space <i>between</i> the 'border-panes'
    <p>This layout was created with only <b>default options</b> - no customization</p>
    <p>Only the <b>applyDefaultStyles</b> option was enabled for <i>basic</i> formatting</p>
    <p>The Close buttons in East/West panes and the buttons below are examples of <b>custom buttons</b></p>

    <p><a href="http://layout.jquery-dev.com/demos.html"><b>Go to the Demos page</b></a></p>

    <p class="buttons">
        <!-- these buttons have event added dynamically in document.ready -->
        <button id="openAllPanes">Open All Panes</button>
        &nbsp;
        <button id="closeAllPanes">Close All Panes</button>
        &nbsp;
        <button id="toggleAllPanes">Toggle All Panes</button>
    </p>

    <p class="buttons">
        <button onclick="myLayout.toggle('north')">Toggle North Pane</button>
        &nbsp;
        <!-- this button has its event added dynamically in document.ready -->
        <button class="south-toggler">Toggle South Pane</button>
    </p>

    <p class="buttons">
        <button onclick="myLayout.hide('east')">Hide East Pane</button>
        &nbsp;
        <button onclick="myLayout.show('east', false)">Unhide East (Closed)</button>
        &nbsp;
        <button onclick="myLayout.show('east')">Unhide East (Open)</button>
    </p>

    <p class="buttons">
        <button onclick="toggleLiveResizing()">Toggle Live-Resizing (all panes)</button>
        &nbsp;
        <button id="btnToggleState" onclick="toggleStateManagement()">Disable State Cookie</button>
        &nbsp;
        <button id="btnReset" onclick="myLayout.loadState(stateResetSettings, true)">Reset State</button>
    </p>

    <p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p>
    <p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p>
    <p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p>
    <p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p><p>...</p>
</div>

</body>
</html>
"""

c_msg = '<p style="padding: 10px; color: red; border: black 2px solid">%s</p>'

def _indent(lines):
    return ' '*TAB + lines.replace('\n', '\n'+' '*TAB)

class DSPOPages(object):
    def __init__(self):
        self.sid = str(uuid.uuid1())
        self.lastpage = None
        self.jsondata = None

    def genindex(self, msg='' ):
        return index_page%{'msg': msg, 'sid': self.sid}

    def gendata(self, msg='' ):
        return data_page%{'msg': msg, 'sid': self.sid}

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
                with open(datapath) as jfile:    
                    data = json.load(jfile)
                page = self.gendata()
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
                    params = dict(urlparse.parse_qsl(query[1], True, True))

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
