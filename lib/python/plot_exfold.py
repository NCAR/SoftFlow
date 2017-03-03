#!/usr/bin/python
'''Plotting script for Extrae folding results
'''

from __future__ import print_function

import os
import sys
import math
import glob
from argparse import ArgumentParser
from collections import OrderedDict
from csv import DictReader
from datetime import datetime

try:
    from  matplotlib import pyplot as plt
    from  matplotlib import colors as mcolors
    from matplotlib.backends.backend_pdf import PdfPages

    colors = { idx:cname for idx, cname in enumerate(mcolors.cnames) }
    pdf = PdfPages('exfold_report.pdf')
except:
    print ('ERROR: matplotlib module is not loaded.')
    sys.exit(-1)

FIELDNAMES = [ 'region', 'group', 'counter', 'xval', 'yval' ]
TITLE_SIZE = 24
SUBTITLE_SIZE = 18
TEXT_SIZE = 14
LABEL_SIZE = 18
LINEWIDTH = 3

cfg = OrderedDict()

def parse_args():

    # argument parsing
    parser = ArgumentParser(description='Plotting Extrae folding results')
    parser.add_argument('folddirs', metavar='folding-dir', type=str, nargs='+', help='Directory containing folded Extrae raw data')
    parser.add_argument('-e', '--event', dest='event', type=str, action='append', default=None, help='Events to use (default: all events)')
    #parser.add_argument('--sum', dest='accumulate', action='store_const', const=sum, default=max, help='sum the integers (default: find the max)')

    args = parser.parse_args()

    # events
    if args.event is None:
        cfg['events'] = True
    else:
        events = []
        for evts in args.event:
            for evt in evts.split(','):
                events.append(evt)
        cfg['events'] = events
   
    # folding dirs
    folddirs = []
    cfg['folddirs'] = folddirs

    # csvfiles
    csvfiles = OrderedDict()
    cfg['csvfiles'] = csvfiles

    # elapsed time
    etimes = OrderedDict()
    cfg['etimes'] = etimes

    # system
    systems = []
    cfg['systems'] = systems

    for folddir in args.folddirs:
        if not os.path.exists(folddir):
            print ('ERROR: can not find input file: %s'%folddir)
            sys.exit(-1)

        absfolddir = os.path.abspath(folddir)
        folddirs.append(absfolddir)
        for pathname in glob.glob('%s/*'%folddir):
            if pathname.endswith('codeblocks.fused.any.any.any.slope.csv'):
                csvfiles[absfolddir] = os.path.abspath(pathname)
            elif pathname.endswith('ratio_per_instruction.gnuplot'):
                with open(pathname, 'r') as f:
                    line = f.readline()
                    etime = line.split('#')[0].split('=')[1].strip()
                    etimes[absfolddir] = etime
            elif pathname.endswith('codeblocks.row'):
                lines = []
                with open(pathname, 'r') as f:
                    lines = f.readlines()
                for curline, nextline in zip(lines[:-1], lines[1:]):
                    if curline.startswith('LEVEL NODE'):
                        if nextline not in systems:
                            systems.append(nextline)
        
    if any(  len(data) == 0 for data in [ cfg['csvfiles'], cfg['etimes'], cfg['systems'] ]):
        print ('ERROR: can not find any folding data. Please check input path(s) in command line.')
        sys.exit(-1)

def read_data():

    # regions
    regions = OrderedDict()
    cfg['regions'] = regions

    # csv data
    csvdata = OrderedDict()
    cfg['csvdata'] = csvdata
    for absfolddir, csvfile in cfg['csvfiles'].items():
        with open(csvfile, 'r') as fcsv:
            reader = DictReader(fcsv, fieldnames=FIELDNAMES, delimiter=';')
            for row in reader:

                if isinstance(cfg['events'], list):
                    if row['counter'] not in cfg['events']:
                        continue
                elif not ( isinstance(cfg['events'], bool) and cfg['events']):
                    continue

                # counter
                if row['counter'] not in csvdata:
                    counter = OrderedDict()
                    csvdata[ row['counter'] ] = counter
                else:
                    counter = csvdata[ row['counter'] ]

                # region
                if row['region'] not in counter:
                    region = OrderedDict()
                    counter[ row['region'] ] = region
                else:
                    region = counter[ row['region'] ]

                if absfolddir not in regions:
                    regions[absfolddir] = row['region']

                # xval and yval
                xval = float(row['xval'])
                yval = float(row['yval'])
                if xval not in region:
                    if xval < 0.01 or xval > 0.99:
                        region[ xval ] = 0
                    elif math.isnan(yval):
                        region[ xval ] = 0
                    else:
                        region[ xval ] = yval
                else:
                    raise Exception('Dupulicated values: %s from %s.'%(str(row), csvfile))

    #import pdb; pdb.set_trace()

def gen_frontpage():

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axis([0, 1, 1, 0])

    ax.text(0.5, 0.3, 'Exfold Report', fontsize=TITLE_SIZE, \
        horizontalalignment='center', verticalalignment='center')

    ax.text(0.5, 0.5, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fontsize=SUBTITLE_SIZE, \
        horizontalalignment='center', verticalalignment='center')

    ax.axis('off')
    fig.tight_layout()
    pdf.savefig(fig)

def gen_summarypage():

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axis([0, 1, 1, 0])

    #ax.text(0.2, 0.1, 'Summary', fontsize=TITLE_SIZE, horizontalalignment='center', verticalalignment='center')
    ax.text(0.1, 0.1, 'Summary', fontsize=TITLE_SIZE, horizontalalignment='left')

    yloc = 0.2

    ax.text(0.05, yloc, '[ Data ]', fontsize=SUBTITLE_SIZE, horizontalalignment='left')

    for idx, folddir in enumerate(cfg['folddirs']):
        line = '%s(%s ms): %s'%(cfg['regions'][folddir], cfg['etimes'][folddir], folddir)
        yloc += 0.05
        if len(line) > 60:
            ax.text(0.1, yloc, '- %s'%line[:60], fontsize=TEXT_SIZE, horizontalalignment='left')
            yloc += 0.05
            ax.text(0.1, yloc, '  %s'%line[60:], fontsize=TEXT_SIZE, horizontalalignment='left')
        else:
            ax.text(0.1, yloc, '- %s'%line, fontsize=TEXT_SIZE, horizontalalignment='left')

    yloc += 0.1
    ax.text(0.05, yloc, '[ System ]', fontsize=SUBTITLE_SIZE, horizontalalignment='left')

    for system in cfg['systems']:
        yloc += 0.05
        if len(system) > 60:
            ax.text(0.1, yloc, '- %s'%system[:60], fontsize=TEXT_SIZE, horizontalalignment='left')
            yloc += 0.05
            ax.text(0.1, yloc, '  %s'%system[60:], fontsize=TEXT_SIZE, horizontalalignment='left')
        else:
            ax.text(0.1, yloc, '- %s'%system, fontsize=TEXT_SIZE, horizontalalignment='left')

    yloc += 0.1
    ax.text(0.05, yloc, '[ Hardware counters ]', fontsize=SUBTITLE_SIZE, horizontalalignment='left')

    counters = [ cnt for cnt in cfg['csvdata'].keys() if not cnt.endswith('per_ins')]
    listcnts = []
    for counter in counters:
        listcnts.append(counter)
        strcnts = ', '.join(listcnts)
        if len(strcnts) < 50: continue
        yloc += 0.05
        ax.text(0.1, yloc, '- %s'%strcnts, fontsize=TEXT_SIZE, horizontalalignment='left')
        listcnts = []

    if len(listcnts) > 0:
        strcnts = ', '.join(listcnts)
        yloc += 0.05
        ax.text(0.1, yloc, '- %s'%strcnts, fontsize=TEXT_SIZE, horizontalalignment='left')

    ax.axis('off')
    fig.tight_layout()
    pdf.savefig(fig)

def gen_plotdescpage():

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axis([0, 1, 1, 0])

    ax.text(0.1, 0.1, 'Plot Description', fontsize=TITLE_SIZE, horizontalalignment='left')


    ax.text(0.5, 0.5, 'T.B.D.', fontsize=TITLE_SIZE, \
        horizontalalignment='center', verticalalignment='center')


    ax.axis('off')
    fig.tight_layout()
    pdf.savefig(fig)

def gen_plotpages():

    for counter, regions in cfg['csvdata'].items():

        fig, ax = plt.subplots(figsize=(8, 6))
        ax2 = fig.add_axes([0.15, 0.1, 0.8, 0.7])

        maxval = 0
        plotdata = OrderedDict()
        for region, vals in regions.items():
            plotdata[region] = (vals.keys(), vals.values())
            maxval = max(maxval, max(plotdata[region][1]))

        ax.text(0.5, 0.95, counter, fontsize=SUBTITLE_SIZE, \
            horizontalalignment='center', verticalalignment='center')
        ax.axis('off')
        
        H = max(0.001, maxval*1.5)
        ax2.axis([0, 100, 0, H])

        ax2.set_xlabel('% elapsed time')
        if counter.find('per_ins') > 0:
            ax2.set_ylabel('events / instruction')
        else:
            ax2.set_ylabel('# events( $\mathregular{10^{6}}$ )')

        plots = []
        labels = []
        for idx, (region, (xvals, yvals)) in enumerate(plotdata.items()):
            plot = ax2.plot([x*100 for x in xvals], yvals, color=colors[idx], linewidth=LINEWIDTH)
            plots.append(plot[0])
            labels.append(region)

        plt.legend(plots, labels)
        #fig.tight_layout()

        pdf.savefig(fig)

def gen_report():

    # front page
    gen_frontpage()
    
    # summary page
    gen_summarypage()

    # plot description page
    #gen_plotdescpage()

    # plot pages
    gen_plotpages()

    pdf.close()

def main():

    # argument parsing
    parse_args()

    # read folding data
    read_data()

    # generate a report
    gen_report()

if __name__ == '__main__':
    sys.exit(main())
