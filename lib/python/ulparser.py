# Universal Logfile Parsing Library
#
# Author : Youngsung Kim
# TODO:
# - remove consumeendline attrib from __CLSNAME__
# - add Unknown_In_CLSNAME class for unparsed line

import os
import re

# cache for dynamically created classes
_classes = {}

DEBUG = False

class LogFile(object):
    def __init__(self, logfile):
        # read log file
        with open(logfile, 'r') as f:
            self.rawlog = f.readlines()

        self.curpos = 0
        self.nlines = len(self.rawlog)

    def hasline(self):
        return self.curpos < self.nlines

    def getline(self):
        return self.rawlog[self.curpos]

    def forward(self):
        if self.curpos < self.nlines:
            self.curpos += 1
        else:
            raise Exception('No more line')

    def backward(self):
        if self.curpos > 0:
            self.curpos -= 1
        else:
            raise Exception('No less line')

class LogBase(object):
    def __init__(self, logfile):
        self.isvalid = False
        self.logfile = logfile
        self.rawline = self.logfile.getline()
        self.process()

    def process(self):
        raise Exception('Can not process at LogBase')

class LogBLine(LogBase):
    line = '^\n$'
    def process(self):
        self.isvalid = re.search(self.line, self.rawline)

class LogLine(LogBase):
    def process(self):
        self.isvalid = re.search(self.line, self.rawline)
        if self.isvalid:
            if hasattr(self.isvalid, 'groupdict'):
                for k, v in self.isvalid.groupdict().iteritems():
                    setattr(self, k, v)

class LogBlock(LogBase):
    def create_subnode(self):

        for subc in self.subcls:
            item = subc(self.logfile)
            if item.isvalid:
                if DEBUG: print 'SUBNODE: ', item, item.rawline
                self.content.append(item)
                break 

        if item.isvalid:
            if isinstance(item, LogBlock) and hasattr(item, 'consumeendline') and item.consumeendline=='False':
                pass
            else:
                self.logfile.forward()
        else:
            print 'Can not parse: %s' % self.logfile.getline()
            import pdb ; pdb.set_trace()
            self.logfile.forward()            

    def search_end(self, patline, line):
        search = None
        clsname = None

        patterns = [ p.strip() for p in patline.split("||") ]
        for pat in patterns:
            if pat.startswith("__") and pat.endswith("__"):
                clsname = pat[2:-2]
                if clsname in _classes:
                    search = re.search(_classes[clsname].begin, line)
                else:
                    raise Exception('%s is not class name'%clsname)
            else:
                search = re.search(pat, line)

            if search: break
            else: clsname = None

        return search, clsname

    def process(self):

        # search the head of a block
        self.isvalid = re.search(self.begin, self.rawline)

        # if found
        if self.isvalid:
            if DEBUG: print 'SELF: ', self, self.rawline

            if not hasattr(self, 'content'):
                self.content = []
            self.logfile.forward()

            # populate attributes
            if hasattr(self.isvalid, 'groupdict'):
                for k, v in self.isvalid.groupdict().iteritems():
                    setattr(self, k, v)

            # search subnodes
            while self.logfile.hasline():
                # if end line
                if hasattr(self, 'end'):
                    endline, beginclsname = self.search_end(self.end, self.logfile.getline())
                    if endline:
                        endclsname = 'End'+self.__class__.__name__
                        if endclsname in _classes:
                            endcls = _classes[endclsname]
                        else:
                            endcls = type('End'+self.__class__.__name__, (object,), {})
                            if not hasattr(endcls, 'attrib'): endcls.attrib = {}
                            _classes[endclsname] = endcls
                        endobj = endcls()
                        self.content.append(endobj)

                        if DEBUG: print 'END: ', endobj, self.logfile.getline()

                        if beginclsname:
                            self.logfile.backward()
                        return

                # create subnode
                self.create_subnode()


class LogRoot(LogBlock):
    subcls = [ LogBLine ]

    def __init__(self, logfile):
        self.content = []
        self.isvalid = True
        self.logfile = logfile

        if DEBUG: print 'ROOT: ', self
        while logfile.hasline():
            self.create_subnode()

class ULParser(object):
    # handle escape less than and greater than
    def prep_xmlfile(self, xmlfile):
        # read xml file
        if os.path.exists(xmlfile):
            with open(xmlfile, 'r') as f:
                src = f.read()
        else:
            src = xmlfile

        dst = ''

        flen = len(src)
        pos = 0
        depth = 0
        quote = None

        while(pos<flen):
            ch = src[pos]
            if quote:
                if ch=='<':
                    dst += '&lt;'
                elif ch=='>':
                    dst += '&gt;'
                elif ch=='"' or ch=="'":
                    if quote==ch:
                        dst += ch
                        quote = None
                else:
                    dst += ch
            else:
                if ch=='<':
                    depth += 1
                elif ch=='>':
                    depth -= 1
                elif ch=='"' or ch=="'":
                    quote = ch
                dst += ch
            pos += 1

        return dst

    def __init__(self, xmlfile, logfile):
        import xml.etree.ElementTree as ET

        # read xml file
        xmlprep = self.prep_xmlfile(xmlfile)
        self.xml = ET.fromstring(xmlprep)
        if self.xml.tag!='Log':
            print 'Root element is not Log'
            sys.exit(-1)

        # construct parser
        for elem in self.xml:
            self.create_class(LogRoot, elem)

        # prase log file
        self.logfile = LogFile(logfile)
        self.root = LogRoot(self.logfile)
 
    def create_class(self, parentcls, node):
        cls = None

        # if class name exists
        if node.tag in _classes:
            cls = _classes[node.tag]

            # update class
            for key, value in node.attrib.items():
                if key in cls.attrib:
                    if value!=cls.attrib[key]:
                        raise Exception('differnt attribute for %s: %s <-> %s' % \
                            str(key), str(value), str(cls.attrib[key]))
                else:
                    cls.attrib[key] = value
        else:
            # block type
            if 'begin' in node.attrib and 'end' in node.attrib:
                node.attrib['subcls'] = [ LogBLine ]
                cls = type(node.tag, (LogBlock,), node.attrib)
                if not hasattr(cls, 'attrib'): cls.attrib = {}
                _classes[node.tag] = cls
                for elem in node:
                    self.create_class(cls, elem)
            # line type
            elif 'line' in node.attrib:
                cls = type(node.tag, (LogLine,), node.attrib)
                if not hasattr(cls, 'attrib'): cls.attrib = {}
                _classes[node.tag] = cls
            else:
                raise Exception('Non-block and non-line type node')

        # generate subclass of a current class
        if cls and parentcls and hasattr(parentcls, 'subcls'):
            if not cls in parentcls.subcls:
                parentcls.subcls.append(cls)


    def walk(self, node=None, depth=-1, _initial_depth=None):
        if node is None:
            node = self.root
        if _initial_depth is None:
            if depth==0:
                return
            _initial_depth = depth
        if not isinstance(node, LogRoot):
            yield node, _initial_depth - depth
        if isinstance(node, LogBlock):
            last_node = node.content[-1]
            last_index = len(node.content)
            if last_node.__class__.__name__.startswith('End'):
                last_index -= 1
            else:
                last_node = None
            if depth != 0:
                for subnode in node.content[:last_index]:
                    for n, n_depth in self.walk(subnode, depth-1, _initial_depth):
                        yield n, n_depth
            if last_node is not None:
                yield last_node, _initial_depth - depth

    def DFS(self, node=None, depth=0):
        if node is None:
            node = self.root

        if hasattr(node, 'content'):
            for subnode in node.content:
                self.DFS(subnode, depth+1)
        else:
            yield node, depth


