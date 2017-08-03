#!/usr/bin/python
'''Plotting script for KGen representation
'''

import os
import sys
import numpy
import random
import scipy
from scipy import stats
from argparse import ArgumentParser
from configparser import ConfigParser
from collections import OrderedDict

try:
    from  matplotlib import pyplot as plt
    from  matplotlib import colors as mcolors
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib import ticker

    colors = { idx:cname for idx, cname in enumerate(mcolors.cnames) }
except:
    print ('ERROR: matplotlib module is not loaded.')
    sys.exit(-1)

TITLE_SIZE = 20
SUBTITLE_SIZE = 16
TEXT_SIZE = 14
LABEL_SIZE = 18
TICKLABEL_SIZE = 18
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
    #parser = ArgumentParser(description='Plotting KGen Representation for Elapsedtime')
    #parser.add_argument('etime', metavar='elapsedtime', type=str, nargs='+', help='INI data file containing elapsed time for original application.')
    #parser.add_argument('--minval', dest='minval', type=float, default=None, help='Minimum value to read')
    #parser.add_argument('--maxval', dest='maxval', type=float, default=None, help='Maximum value to read')
    #parser.add_argument('kernel', metavar='kernel', type=str, nargs=1, help='KGen kernel output containing elapsed time.')
    #parser.add_argument('-e', '--event', dest='event', type=str, action='append', default=None, help='Events to use (default: all events)')
    #parser.add_argument('-t', '--time', dest='etime', action='store_true', default=False, help='Add elapsed time in plot (default: No)')
    #parser.add_argument('--sum', dest='accumulate', action='store_const', const=sum, default=max, help='sum the integers (default: find the max)')

    #args = parser.parse_args()

#    cfg['app'] = os.path.abspath(args.etime[0])
#    cfg['runfiles'] = [ os.path.abspath(runfile) for runfile in args.etime[1:] ]
#    cfg['minval'] = args.minval
#    cfg['maxval'] = args.maxval

    prjpath = '/glade/p/tdd/asap/kgen_data/lapack_svd'
    cfg['app'] = '%s/model.ini'%prjpath
    cfg['runfiles'] = [ '%s/run.txt'%prjpath ]
    cfg['minval'] = None #0.003
    cfg['maxval'] = None #0.005 

    if not os.path.exists(cfg['app']):
        print ('ERROR: can not find INI file containing elapsed time for original application: %s'%cfg['app'])
        sys.exit(-1)

    if any(not os.path.exists(runfile) for runfile in cfg['runfiles']):
        print ('ERROR: can not find KGen kernel output file containing elapsed time: %s'%str(cfg['runfiles']))
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


    # read kernels
    cfg['kernels'] = {}
    for runfile in cfg['runfiles']:
        kernel_data = {}
        cfg['kernels'][runfile] = kernel_data
        etimes_kernel = []
        kernel_data['etimes_kernel'] = etimes_kernel
        with open(runfile, 'r') as fk:
            for line in fk:
                pos = line.find(SEARCH_TEXT)
                if pos > 0:
                    etimeval = float(line[(pos+LEN_SEARCH_TEXT):]) * 1.0E-6
                    if cfg['minval'] is not None and etimeval < cfg['minval']:
                        continue
                    if cfg['maxval'] is not None and etimeval > cfg['maxval']:
                        continue
                    etimes_kernel.append(etimeval)
                    cfg['etimemin'] = min(cfg['etimemin'], etimeval)
                    cfg['etimemax'] = max(cfg['etimemax'], etimeval)

def normalize_samples(samples, size=None):
    minval = min(samples)
    maxval = max(samples)
    sumval = maxval + minval
    difval = maxval - minval
    nsamples = len(samples)

    newvals = []
    for sample in samples:
        newvals.append( (2 * sample - sumval) / difval )
        
    if size is not None:
        repeat = size - len(newvals)
        while(repeat > 0):
            newvals.append(random.choice(newvals))
            repeat -= 1

    return newvals

def gen_plotpages():

    scale_x = 1e-3
    ticks_x = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x/scale_x))


    pdf = PdfPages('etime_lapack.pdf')

    app_norm_etimes = normalize_samples(cfg['etimes_app'])
    app_nsamples = len(cfg['etimes_app'])

    fig, (axapp, axkernel) = plt.subplots(1, 2, figsize=(12,6))

    #fig.tight_layout()
    bins = numpy.linspace(cfg['etimemin'], cfg['etimemax'], 50)
    axapp.hist(cfg['etimes_app'], bins, alpha=0.5, label='app')
    axapp.set_title('LAPACK SVD\nwith an increasing size of workload', fontsize=TITLE_SIZE)
    axapp.set_xlabel('Elapsed time (ms)', fontsize=LABEL_SIZE)
    axapp.set_ylabel('Frequency', fontsize=LABEL_SIZE)
    for tick in axapp.xaxis.get_major_ticks():
        tick.label.set_fontsize(TICKLABEL_SIZE) 
    for tick in axapp.yaxis.get_major_ticks():
        tick.label.set_fontsize(TICKLABEL_SIZE) 
    axapp.xaxis.set_major_formatter(ticks_x)
    #plt.legend(loc='upper right')

    filepath = cfg['kernels'].keys()[0]
    kernel_data = cfg['kernels'].values()[0]

    kernel_nsamples = len(kernel_data['etimes_kernel'])

    bins = numpy.linspace(cfg['etimemin'], cfg['etimemax'], 50)
    axkernel.hist(kernel_data['etimes_kernel'], bins, alpha=0.5, label='kernel')
    axkernel.set_title('LAPACK SVD kernel', fontsize=TITLE_SIZE)
    axkernel.set_xlabel('Elapsed time (ms)', fontsize=LABEL_SIZE)
    #axkernel.set_ylabel('Frequency', fontsize=LABEL_SIZE)
    for tick in axkernel.xaxis.get_major_ticks():
        tick.label.set_fontsize(TICKLABEL_SIZE) 
    for tick in axkernel.yaxis.get_major_ticks():
        tick.label.set_fontsize(TICKLABEL_SIZE) 
    axkernel.xaxis.set_major_formatter(ticks_x)
    #plt.legend(loc='upper right')
    #fig.autofmt_xdate()
    pdf.savefig(fig)

    pdf.close()

    pdf = PdfPages('etime_lapack_stat.pdf')

    fig, axstat = plt.subplots(figsize=(8, 6))
    axstat.axis([0, 1, 1, 0])
    axstat.axis('off')
    axstat.text(0.1, 0.1, 'Statistics of two samples', fontsize=TITLE_SIZE, horizontalalignment='left')

    stat_lines = []

    minval_app = numpy.amin(cfg['etimes_app']) 
    minval_kernel = numpy.amin(kernel_data['etimes_kernel']) 
    minval_diff = (minval_kernel - minval_app) / minval_app
    stat_lines.append( ('Minimum', minval_app, minval_kernel, minval_diff) ) # Minumum

    maxval_app = numpy.amax(cfg['etimes_app']) 
    maxval_kernel = numpy.amax(kernel_data['etimes_kernel']) 
    maxval_diff = (maxval_kernel - maxval_app) / maxval_app
    stat_lines.append( ('Maximum', maxval_app, maxval_kernel, maxval_diff )) # Maximum

    median_app = numpy.median(cfg['etimes_app']) 
    median_kernel = numpy.median(kernel_data['etimes_kernel']) 
    median_diff = (median_kernel - median_app) / median_app
    stat_lines.append( ('Median', median_app, median_kernel, median_diff )) # Maximum

    average_app = numpy.average(cfg['etimes_app']) 
    average_kernel = numpy.average(kernel_data['etimes_kernel']) 
    average_diff = (average_kernel - average_app) / average_app
    stat_lines.append( ('Average', average_app, average_kernel, average_diff )) # Maximum

    mean_app = numpy.mean(cfg['etimes_app']) 
    mean_kernel = numpy.mean(kernel_data['etimes_kernel']) 
    mean_diff = (mean_kernel - mean_app) / mean_app
    stat_lines.append( ('Mean', mean_app, mean_kernel, mean_diff )) # Maximum

    kernel_norm_etimes = normalize_samples(kernel_data['etimes_kernel'], size=app_nsamples)

    #std_app = numpy.std(cfg['etimes_app']) 
    std_app = numpy.std(app_norm_etimes) 
    #std_kernel = numpy.std(kernel_data['etimes_kernel']) 
    std_kernel = numpy.std(kernel_norm_etimes) 
    std_diff = (std_kernel - std_app) / std_app
    stat_lines.append( ('SVar', std_app, std_kernel, std_diff )) # Maximum

    #var_app = numpy.var(cfg['etimes_app']) 
    #var_app = numpy.var(app_norm_etimes) 
    #var_kernel = numpy.var(kernel_data['etimes_kernel']) 
    #var_kernel = numpy.var(kernel_norm_etimes) 
    #var_diff = (var_kernel - var_app) / var_app
    #stat_lines.append( ('Variance', var_app, var_kernel, var_diff )) # Maximum

    skew_app = stats.skew(app_norm_etimes)
    skew_kernel = stats.skew(kernel_norm_etimes)
    skew_diff = (skew_kernel - skew_app) / skew_app
    stat_lines.append( ('Skew', skew_app, skew_kernel, skew_diff ))

    kurtosis_app = stats.kurtosis(app_norm_etimes)
    kurtosis_kernel = stats.kurtosis(kernel_norm_etimes)
    kurtosis_diff = (kurtosis_kernel - kurtosis_app) / kurtosis_app
    stat_lines.append( ('Kurtosis', kurtosis_app, kurtosis_kernel, kurtosis_diff ))

    yloc = 0.2

    axstat.text(0.1, yloc, 'Statistic   |   application     |   kernel    |  difference', fontsize=TEXT_SIZE, horizontalalignment='left')
    yloc += 0.05
    axstat.text(0.1, yloc, '===============================', fontsize=TEXT_SIZE, horizontalalignment='left')
    yloc += 0.05

    for idx, (item, appval, kernelval, diff) in enumerate(stat_lines):
        percent_diff = '{:.1%}'.format(diff)
        line = '%s: %f    %f    %s'%(item, appval, kernelval, percent_diff)
        yloc += 0.05
        axstat.text(0.1, yloc, line, fontsize=TEXT_SIZE, horizontalalignment='left')

    #yloc += 0.05
    ##correlate = numpy.correlate(cfg['etimes_app'], kernel_data['etimes_kernel']) 
    #correlate = numpy.correlate(app_norm_etimes, kernel_norm_etimes) 
    #axstat.text(0.1, yloc, 'Correlation: %f'%correlate[0], fontsize=TEXT_SIZE, horizontalalignment='left')

    pdf.savefig(fig)

    pdf.close()

def gen_report():

    # front page
    #gen_frontpage()
    
    # summary page
    #gen_summarypage()

    # plot description page
    #gen_plotdescpage()

    # plot pages
    gen_plotpages()


def main():

    # argument parsing
    parse_args()

    # read folding data
    read_data()

    # generate a report
    gen_report()

if __name__ == '__main__':
    sys.exit(main())
