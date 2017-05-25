#!/usr/bin/python
'''Plotting script for KGen representation
'''

import os
import sys
import numpy
from argparse import ArgumentParser
from configparser import ConfigParser
from collections import OrderedDict

try:
    from  matplotlib import pyplot as plt
    from  matplotlib import colors as mcolors
    from matplotlib.backends.backend_pdf import PdfPages

    colors = { idx:cname for idx, cname in enumerate(mcolors.cnames) }
    pdf = PdfPages('etime_report.pdf')
except:
    print ('ERROR: matplotlib module is not loaded.')
    sys.exit(-1)

TITLE_SIZE = 20
SUBTITLE_SIZE = 16
TEXT_SIZE = 14
LABEL_SIZE = 18
LINEWIDTH = 3

SEARCH_TEXT = ': Time per call (usec):'
LEN_SEARCH_TEXT = len(SEARCH_TEXT)

cfg = OrderedDict()

def normalized(a, axis=-1, order=2):
    l2 = numpy.atleast_1d(numpy.linalg.norm(a, order, axis))
    l2[l2==0] = 1
    return a / numpy.expand_dims(l2, axis)

def parse_args():

    # argument parsing
    parser = ArgumentParser(description='Plotting KGen Representation for Elapsedtime')
    parser.add_argument('etime', metavar='elapsedtime', type=str, nargs=2, help='INI data file containing elapsed time for original application.')
    #parser.add_argument('kernel', metavar='kernel', type=str, nargs=1, help='KGen kernel output containing elapsed time.')
    #parser.add_argument('-e', '--event', dest='event', type=str, action='append', default=None, help='Events to use (default: all events)')
    #parser.add_argument('-t', '--time', dest='etime', action='store_true', default=False, help='Add elapsed time in plot (default: No)')
    #parser.add_argument('--sum', dest='accumulate', action='store_const', const=sum, default=max, help='sum the integers (default: find the max)')

    args = parser.parse_args()

    cfg['app'] = os.path.abspath(args.etime[0])
    cfg['kernel'] = os.path.abspath(args.etime[1])
        
    if not os.path.exists(cfg['app']):
        print ('ERROR: can not find INI file containing elapsed time for original application: %s'%cfg['app'])
        sys.exit(-1)

    if not os.path.exists(cfg['kernel']):
        print ('ERROR: can not find KGen kernel output file containing elapsed time: %s'%cfg['kernel'])
        sys.exit(-1)

def read_data():

    # read app
    appini = ConfigParser()
    appini.optionxform = str
    appini.read(cfg['app'])

    cfg['etimemin'] = 1.0E100
    cfg['etimemax'] = 0.0

    try:
        etimemin = float(appini.get('elapsedtime.summary', 'minimum_elapsedtime').strip())
        etimemax = float(appini.get('elapsedtime.summary', 'maximum_elapsedtime').strip())
        netimes = int(appini.get('elapsedtime.summary', 'number_elapsedtimes').strip())
        etimediff = etimemax - etimemin
        etimeres = float(appini.get('elapsedtime.summary', 'resolution_elapsedtime').strip())

        etimes_app = []
        cfg['etimes_app'] = etimes_app
        for opt in appini.options('elapsedtime.elapsedtime'):
            start, stop = appini.get('elapsedtime.elapsedtime', opt).split(',')
            estart = float(start)
            eend = float(stop)
            etimeval = eend - estart
            etimes_app.append(etimeval)
            cfg['etimemin'] = min(cfg['etimemin'], etimeval)
            cfg['etimemax'] = max(cfg['etimemax'], etimeval)

    except Exception as e:
        raise Exception('Please check the format of elapsedtime file: %s'%str(e))


    # read kernel
    etimes_kernel = []
    cfg['etimes_kernel'] = etimes_kernel
    with open(cfg['kernel'], 'r') as fk:
        for line in fk:
            pos = line.find(SEARCH_TEXT)
            if pos > 0:
                etimeval = float(line[(pos+LEN_SEARCH_TEXT):]) * 1.0E-6
                etimes_kernel.append(etimeval)
                cfg['etimemin'] = min(cfg['etimemin'], etimeval)
                cfg['etimemax'] = max(cfg['etimemax'], etimeval)

def gen_plotpages():


    fig, axapp = plt.subplots(figsize=(8, 6))
    #fig.tight_layout()
    bins = numpy.linspace(cfg['etimemin'], cfg['etimemax'], 50)
    axapp.hist(cfg['etimes_app'], bins, alpha=0.5, label='app')
    axapp.set_title('Elapsed time of longwave-RRTMGP', fontsize=TITLE_SIZE)
    axapp.set_xlabel('elapsed time (sec)')
    #plt.legend(loc='upper right')
    pdf.savefig(fig)

    fig, axkernel = plt.subplots(figsize=(8, 6))
    bins = numpy.linspace(cfg['etimemin'], cfg['etimemax'], 50)
    axkernel.hist(cfg['etimes_kernel'], bins, alpha=0.5, label='kernel')
    axkernel.set_title('Elapsed time of Longwave-RRTMGP kernel', fontsize=TITLE_SIZE)
    axkernel.set_xlabel('elapsed time (sec)')
    #plt.legend(loc='upper right')
    pdf.savefig(fig)

    fig, axstat = plt.subplots(figsize=(8, 6))
    axstat.axis([0, 1, 1, 0])
    axstat.axis('off')
    axstat.text(0.1, 0.1, 'Statistics of two samples', fontsize=TITLE_SIZE, horizontalalignment='left')

    stats = []

    minval_app = numpy.amin(cfg['etimes_app']) 
    minval_kernel = numpy.amin(cfg['etimes_kernel']) 
    minval_diff = abs(minval_kernel - minval_app) / minval_app
    stats.append( ('Minimum', minval_app, minval_kernel, minval_diff) ) # Minumum

    maxval_app = numpy.amax(cfg['etimes_app']) 
    maxval_kernel = numpy.amax(cfg['etimes_kernel']) 
    maxval_diff = abs(maxval_kernel - maxval_app) / maxval_app
    stats.append( ('Maximum', maxval_app, maxval_kernel, maxval_diff )) # Maximum

    median_app = numpy.median(cfg['etimes_app']) 
    median_kernel = numpy.median(cfg['etimes_kernel']) 
    median_diff = abs(median_kernel - median_app) / median_app
    stats.append( ('Median', median_app, median_kernel, median_diff )) # Maximum

    average_app = numpy.average(cfg['etimes_app']) 
    average_kernel = numpy.average(cfg['etimes_kernel']) 
    average_diff = abs(average_kernel - average_app) / average_app
    stats.append( ('Average', average_app, average_kernel, average_diff )) # Maximum

    mean_app = numpy.mean(cfg['etimes_app']) 
    mean_kernel = numpy.mean(cfg['etimes_kernel']) 
    mean_diff = abs(mean_kernel - mean_app) / mean_app
    stats.append( ('Mean', mean_app, mean_kernel, mean_diff )) # Maximum

    std_app = numpy.std(cfg['etimes_app']) 
    std_kernel = numpy.std(cfg['etimes_kernel']) 
    std_diff = abs(std_kernel - std_app) / std_app
    stats.append( ('SVar', std_app, std_kernel, std_diff )) # Maximum

    var_app = numpy.var(cfg['etimes_app']) 
    var_kernel = numpy.var(cfg['etimes_kernel']) 
    var_diff = abs(var_kernel - var_app) / var_app
    stats.append( ('Variance', var_app, var_kernel, var_diff )) # Maximum

    yloc = 0.2
    for idx, (item, appval, kernelval, diff) in enumerate(stats):
        percent_diff = '{:.1%}'.format(diff)
        line = '%s: %f    %f    %s'%(item, appval, kernelval, percent_diff)
        yloc += 0.05
        axstat.text(0.1, yloc, line, fontsize=TEXT_SIZE, horizontalalignment='left')

    yloc += 0.05
    correlate = numpy.correlate(cfg['etimes_app'], cfg['etimes_kernel']) 
    axstat.text(0.1, yloc, 'Correlation: %f'%correlate[0], fontsize=TEXT_SIZE, horizontalalignment='left')

    pdf.savefig(fig)

def gen_report():

    # front page
    #gen_frontpage()
    
    # summary page
    #gen_summarypage()

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
