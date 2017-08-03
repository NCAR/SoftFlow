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

SEARCH_TEXT = 'TCM (L1,L2,L3):'
LEN_SEARCH_TEXT = len(SEARCH_TEXT)

cfg = OrderedDict()

def normalized(a, axis=-1, order=2):
    l2 = numpy.atleast_1d(numpy.linalg.norm(a, order, axis))
    l2[l2==0] = 1
    return a / numpy.expand_dims(l2, axis)

def parse_args():

    # argument parsing
    #parser = ArgumentParser(description='Plotting KGen Representation for Elapsedtime')
    #parser.add_argument('papi', metavar='elapsedtime', type=str, nargs='+', help='INI data file containing elapsed time for original application.')
    #parser.add_argument('--minval', dest='minval', type=float, default=None, help='Minimum value to read')
    #parser.add_argument('--maxval', dest='maxval', type=float, default=None, help='Maximum value to read')
    #parser.add_argument('kernel', metavar='kernel', type=str, nargs=1, help='KGen kernel output containing elapsed time.')
    #parser.add_argument('-e', '--event', dest='event', type=str, action='append', default=None, help='Events to use (default: all events)')
    #parser.add_argument('-t', '--time', dest='papi', action='store_true', default=False, help='Add elapsed time in plot (default: No)')
    #parser.add_argument('--sum', dest='accumulate', action='store_const', const=sum, default=max, help='sum the integers (default: find the max)')

    #args = parser.parse_args()

#    cfg['app'] = os.path.abspath(args.papi[0])
#    cfg['runfiles'] = [ os.path.abspath(runfile) for runfile in args.papi[1:] ]
#    cfg['minval'] = args.minval
#    cfg['maxval'] = args.maxval

    prjpath = '/glade/p/tdd/asap/kgen_data/lapack_svd_papi'
    cfg['app'] = '%s/0.0'%prjpath
    cfg['runfile'] = '%s/run.txt'%prjpath
    cfg['minval'] = None #0.003
    cfg['maxval'] = None #0.005 

    if not os.path.exists(cfg['app']):
        print ('ERROR: can not find INI file containing elapsed time for original application: %s'%cfg['app'])
        sys.exit(-1)

    if not os.path.exists(cfg['runfile']):
        print ('ERROR: can not find KGen kernel output file containing elapsed time: %s'%str(cfg['runfile']))
        sys.exit(-1)

def read_data():

    # read app

    cfg['papimin'] = [ 1E100, 1E100, 1E100 ]
    cfg['papimax'] = [ 0, 0 , 0 ]

    papis_app = [ [], [], [] ]
    cfg['papis_app'] = papis_app
    with open(cfg['app'], 'r') as fa:
        for line in fa.read().splitlines():
            invoke, L1, L2, L3 = line.split()
            papis_app[0].append(int(L1))
            papis_app[1].append(int(L2))
            papis_app[2].append(int(L3))
            cfg['papimin'][0] = min(cfg['papimin'][0], int(L1))
            cfg['papimin'][1] = min(cfg['papimin'][1], int(L2))
            cfg['papimin'][2] = min(cfg['papimin'][2], int(L3))
            cfg['papimax'][0] = max(cfg['papimax'][0], int(L1))
            cfg['papimax'][1] = max(cfg['papimax'][1], int(L2))
            cfg['papimax'][2] = max(cfg['papimax'][2], int(L3))


    # read kernels
    papis_kernel = [ [], [], [] ]
    cfg['papis_kernel'] = papis_kernel
    with open(cfg['runfile'], 'r') as fk:
        for line in fk:
            pos = line.find(SEARCH_TEXT)
            if pos >= 0:
                L1, L2, L3 = line[(pos+LEN_SEARCH_TEXT):].split()
                #if cfg['minval'] is not None and papival < cfg['minval']:
                #    continue
                #if cfg['maxval'] is not None and papival > cfg['maxval']:
                #    continue
                papis_kernel[0].append(int(L1))
                papis_kernel[1].append(int(L2))
                papis_kernel[2].append(int(L3))
                cfg['papimin'][0] = min(cfg['papimin'][0], int(L1))
                cfg['papimin'][1] = min(cfg['papimin'][1], int(L2))
                cfg['papimin'][2] = min(cfg['papimin'][2], int(L3))
                cfg['papimax'][0] = max(cfg['papimax'][0], int(L1))
                cfg['papimax'][1] = max(cfg['papimax'][1], int(L2))
                cfg['papimax'][2] = max(cfg['papimax'][2], int(L3))


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

def gen_plotpages(idx, axapp, axkernel, typestr, scale_x, x_unit, papimin, papimax, papis_app, papis_kernel):
    panels = { 0: ('a', 'b'), 1: ('c', 'd'), 2: ('e', 'f') }

    ticks_x = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x/scale_x))

    app_norm_papis = normalize_samples(papis_app)
    app_nsamples = len(papis_app)

    #fig.tight_layout()
    bins = numpy.linspace(papimin, papimax, 50)
    axapp.hist(papis_app, bins, alpha=0.5, label='app')
    if idx == 0:
        axapp.set_title('LAPACK SVD on test program', fontsize=TITLE_SIZE)
    #axapp.set_title('LAPACK SVD\nwith an increasing size of workload', fontsize=TITLE_SIZE)
    axapp.set_xlabel('%s cache misses %s\n(%s)'%(typestr, x_unit, panels[idx][0]), fontsize=LABEL_SIZE)
    axapp.set_ylabel('Frequency', fontsize=LABEL_SIZE)
    for tick in axapp.xaxis.get_major_ticks():
        tick.label.set_fontsize(TICKLABEL_SIZE) 
    for tick in axapp.yaxis.get_major_ticks():
        tick.label.set_fontsize(TICKLABEL_SIZE) 
    axapp.xaxis.set_major_formatter(ticks_x)
    #plt.legend(loc='upper right')

    kernel_nsamples = len(papis_kernel)

    bins = numpy.linspace(papimin, papimax, 50)
    axkernel.hist(papis_kernel, bins, alpha=0.5, label='kernel')
    if idx == 0:
        axkernel.set_title('LAPACK SVD on kernel', fontsize=TITLE_SIZE)
    axkernel.set_xlabel('%s cache misses %s\n(%s)'%(typestr, x_unit, panels[idx][1]), fontsize=LABEL_SIZE)
    #axkernel.set_ylabel('Frequency', fontsize=LABEL_SIZE)
    for tick in axkernel.xaxis.get_major_ticks():
        tick.label.set_fontsize(TICKLABEL_SIZE) 
    for tick in axkernel.yaxis.get_major_ticks():
        tick.label.set_fontsize(TICKLABEL_SIZE) 
    axkernel.xaxis.set_major_formatter(ticks_x)
    #plt.legend(loc='upper right')
    #fig.autofmt_xdate()
#
#    pdf = PdfPages('papi_lapack_stat_%s.pdf'%typestr)
#
#    fig, axstat = plt.subplots(figsize=(8, 6))
#    axstat.axis([0, 1, 1, 0])
#    axstat.axis('off')
#    axstat.text(0.1, 0.1, 'Statistics of two samples', fontsize=TITLE_SIZE, horizontalalignment='left')
#
#    stat_lines = []
#
#    minval_app = numpy.amin(papis_app) 
#    minval_kernel = numpy.amin(papis_kernel) 
#    if minval_app != 0:
#        minval_diff = (minval_kernel - minval_app) / float(minval_app)
#    else:
#        minval_diff = None
#    stat_lines.append( ('Minimum', minval_app, minval_kernel, minval_diff) ) # Minumum
#
#    maxval_app = numpy.amax(papis_app) 
#    maxval_kernel = numpy.amax(papis_kernel) 
#    if maxval_app != 0:
#        maxval_diff = (maxval_kernel - maxval_app) / float(maxval_app)
#    else:
#        maxval_diff = None
#    stat_lines.append( ('Maximum', maxval_app, maxval_kernel, maxval_diff )) # Maximum
#
#    median_app = numpy.median(papis_app) 
#    median_kernel = numpy.median(papis_kernel) 
#    if median_app != 0:
#        median_diff = (median_kernel - median_app) / float(median_app)
#    else:
#        median_diff = None
#    stat_lines.append( ('Median', median_app, median_kernel, median_diff )) # Maximum
#
#    average_app = numpy.average(papis_app) 
#    average_kernel = numpy.average(papis_kernel) 
#    if average_app != 0:
#        average_diff = (average_kernel - average_app) / float(average_app)
#    else:
#        average_diff = None
#    stat_lines.append( ('Average', average_app, average_kernel, average_diff )) # Maximum
#
#    mean_app = numpy.mean(papis_app) 
#    mean_kernel = numpy.mean(papis_kernel) 
#    if mean_app != 0:
#        mean_diff = (mean_kernel - mean_app) / float(mean_app)
#    else:
#        mean_diff = None
#    stat_lines.append( ('Mean', mean_app, mean_kernel, mean_diff )) # Maximum
#
#    kernel_norm_papis = normalize_samples(papis_kernel, size=app_nsamples)
#
#    #std_app = numpy.std(cfg['papis_app']) 
#    std_app = numpy.std(app_norm_papis) 
#    #std_kernel = numpy.std(kernel_data['papis_kernel']) 
#    std_kernel = numpy.std(kernel_norm_papis) 
#    std_diff = (std_kernel - std_app) / std_app
#    stat_lines.append( ('SVar', std_app, std_kernel, std_diff )) # Maximum
#
#    #var_app = numpy.var(cfg['papis_app']) 
#    #var_app = numpy.var(app_norm_papis) 
#    #var_kernel = numpy.var(kernel_data['papis_kernel']) 
#    #var_kernel = numpy.var(kernel_norm_papis) 
#    #var_diff = (var_kernel - var_app) / var_app
#    #stat_lines.append( ('Variance', var_app, var_kernel, var_diff )) # Maximum
#
#    skew_app = stats.skew(app_norm_papis)
#    skew_kernel = stats.skew(kernel_norm_papis)
#    skew_diff = (skew_kernel - skew_app) / skew_app
#    stat_lines.append( ('Skew', skew_app, skew_kernel, skew_diff ))
#
#    kurtosis_app = stats.kurtosis(app_norm_papis)
#    kurtosis_kernel = stats.kurtosis(kernel_norm_papis)
#    kurtosis_diff = (kurtosis_kernel - kurtosis_app) / kurtosis_app
#    stat_lines.append( ('Kurtosis', kurtosis_app, kurtosis_kernel, kurtosis_diff ))
#
#    yloc = 0.2
#
#    axstat.text(0.1, yloc, 'Statistic   |   application     |   kernel    |  difference', fontsize=TEXT_SIZE, horizontalalignment='left')
#    yloc += 0.05
#    axstat.text(0.1, yloc, '===============================', fontsize=TEXT_SIZE, horizontalalignment='left')
#    yloc += 0.05
#
#    for idx, (item, appval, kernelval, diff) in enumerate(stat_lines):
#        if diff is not None:
#            percent_diff = '{:.1%}'.format(diff)
#        else:
#            percent_diff = 'N.A.'
#        line = '%s: %f    %f    %s'%(item, appval, kernelval, percent_diff)
#        yloc += 0.05
#        axstat.text(0.1, yloc, line, fontsize=TEXT_SIZE, horizontalalignment='left')
#
#    #yloc += 0.05
#    ##correlate = numpy.correlate(cfg['papis_app'], kernel_data['papis_kernel']) 
#    #correlate = numpy.correlate(app_norm_papis, kernel_norm_papis) 
#    #axstat.text(0.1, yloc, 'Correlation: %f'%correlate[0], fontsize=TEXT_SIZE, horizontalalignment='left')
#
#    pdf.savefig(fig)
#
#    pdf.close()

def gen_report():

    # front page
    #gen_frontpage()
    
    # summary page
    #gen_summarypage()

    # plot description page
    #gen_plotdescpage()

    typestr = [ 'L1', 'L2', 'L3' ]
    scale_x = [ 1E6, 1E6, 1E3 ]
    x_unit =  [ '(Unit=1.0E6)', '(Unit=1.0E6)', '(Unit=1.0E3)' ]

    pdf = PdfPages('papi_lapack.pdf')



    fig, ax = plt.subplots(3, 2, figsize=(12,18))
    plt.tight_layout(pad=9.0, w_pad=5.0, h_pad=7.0)

    # plot pages
    for idx in range(3):
        gen_plotpages(idx, ax[idx][0], ax[idx][1], typestr[idx], scale_x[idx], x_unit[idx], cfg['papimin'][idx], cfg['papimax'][idx],
            cfg['papis_app'][idx], cfg['papis_kernel'][idx])

    pdf.savefig(fig)

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
