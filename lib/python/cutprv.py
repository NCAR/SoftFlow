#!/usr/bin/python
'''Plotting script for Extrae folding results
'''
from __future__ import print_function

import os
import sys
import subprocess
from argparse import ArgumentParser
#from collections import OrderedDict
#from csv import DictReader
#from datetime import datetime


cutxml = '''<?xml version="1.0" encoding="UTF-8"?>
<config>
  <!-- CUTTER OPTIONS -->
  <cutter>
    <tasks>%s</tasks>
    <max_trace_size>0</max_trace_size>
    <by_time>0</by_time>
    <minimum_time>0</minimum_time>
    <maximum_time>100</maximum_time>
    <minimum_time_percentage>0</minimum_time_percentage>
    <maximum_time_percentage>100</maximum_time_percentage>
    <original_time>0</original_time>
    <break_states>1</break_states>
    <remove_first_states>0</remove_first_states>
    <remove_last_states>0</remove_last_states>
    <keep_events>0</keep_events>
  </cutter>
</config>
'''

TITLE_SIZE = 24
SUBTITLE_SIZE = 18
TEXT_SIZE = 14
LABEL_SIZE = 18
LINEWIDTH = 3

cfg = {}

def parse_args():

    # argument parsing
    parser = ArgumentParser(description='Cutting Extrae trace data')
    parser.add_argument('prvfile', metavar='prvfile', type=str, nargs=1, help='prv file containing folded Extrae raw data')
    parser.add_argument('-r', '--ranks', dest='ranks', type=str, action='append', default=['1'], help='Rank number to extract (default: 1)')
    parser.add_argument('-c', '--cut', dest='cut', type=str, default=None, help='Cutting command (default: None)')
    parser.add_argument('-o', '--out', dest='out', type=str, default=None, help='Cutting command (default: None)')

    args = parser.parse_args()

    # cori on NERSC only
    paraver_home = '/usr/common/software/paraver/4.6.2b/wxparaver-4.6.2-linux-x86_64'
    cut_exec = '%s/bin/paramedir'%paraver_home

    cfg['prvpath'] = args.prvfile[0]
    cfg['prvfile'] = os.path.basename(args.prvfile[0])

    cfg['folding'] = '/global/homes/g/grnydawn/opt/folding/1.0.2/bin/folding'

    if args.out is None:
        cfg['out'] = os.path.dirname(args.folddir)
    else:
        cfg['out'] = args.out

    if args.ranks is None:
        cfg['ranks'] = '1'
    else:
        cfg['ranks'] = args.ranks

    if args.cut is None:
        cfg['cut'] = cut_exec
    else:
        cfg['cut'] = args.cut

def cut_data():

    for rank in cfg['ranks']:
        sr = rank.split('-')
        if len(sr) == 2:
            begin = int(sr[0])
            end = int(sr[1])
        elif len(sr) == 1:
            begin = int(sr[0])
            end = begin + 1

        for idx in range(begin, end):
            try:
                # mkdir dir
                outdir = '%s/%d'%(cfg['out'], idx)
                subprocess.call('mkdir -p %s'%outdir, shell=True)

                # create xml file
                xmlfile = '%s/cut.xml'%outdir
                with open(xmlfile, 'w') as f:
                    f.write(cutxml%idx)

                # cut prv file
                cutprvfile = '%s/cut.%s'%(outdir, cfg['prvfile'])
                cmd = '%s -c -o %s %s %s'%(cfg['cut'], cutprvfile, cfg['prvpath'], xmlfile)
                subprocess.call(cmd, shell=True)

                # fold prv file
                cmd = 'cd %s; %s cut.%s "User function"'%(outdir, cfg['folding'], cfg['prvfile'])
                subprocess.call(cmd, shell=True)
            except:
                pass

    #import pdb; pdb.set_trace()

def main():

    # argument parsing
    parse_args()

    # read folding data
    cut_data()

if __name__ == '__main__':
    sys.exit(main())
