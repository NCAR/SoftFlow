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
    from matplotlib import pyplot as plt
    from matplotlib import colors as mcolors
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
    #parser.add_argument('-o', '--output', dest='output', type=str, default='etime_report.pdf', help='Output filename')
    #parser.add_argument('-t', '--title', dest='title', type=str, default='Elapsedtime Report', help='Plot title')
    #parser.add_argument('kernel', metavar='kernel', type=str, nargs=1, help='KGen kernel output containing elapsed time.')
    #parser.add_argument('-e', '--event', dest='event', type=str, action='append', default=None, help='Events to use (default: all events)')
    #parser.add_argument('-t', '--time', dest='etime', action='store_true', default=False, help='Add elapsed time in plot (default: No)')
    #parser.add_argument('--sum', dest='accumulate', action='store_const', const=sum, default=max, help='sum the integers (default: find the max)')

    #args = parser.parse_args()

    mg2path = '/glade/p/tdd/asap/kgen_data/cesm_mg2'

    cfg['mg2path'] = mg2path 
    cfg['app'] = '%s/model.ini'%mg2path 
    #cfg['runfiles'] = [ '%s/%s'%(mg2path, etime) for etime in ( 'run_ys_1_0M.txt', 'run_ys_30_0M.txt', 'run_ys_30_random.txt' ) ]
    cfg['runfiles'] = [ '%s/%s'%(mg2path, etime) for etime in ( 'run_ys_1_0M.txt', 'run_ys_30_0aM.txt', 'run_ys_30_rand1M.txt' ) ]
    cfg['minval'] = 0.0
    cfg['maxval'] = 0.003

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

    #cfg['etimemin'] = 1.0E100
    #cfg['etimemax'] = 0.0
    cfg['etimemin'] = 0
    cfg['etimemax'] = 0.003

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

    app_data = cfg['etimes_app']
    filepath = '%s/run_ys_1_0M.txt'%cfg['mg2path']
    kernel_data = cfg['kernels'][filepath]

    pdf = PdfPages('etime_mg2_org.pdf')

    fig, (axapp, axkernel) = plt.subplots(1, 2, figsize=(12,6))

    #fig.tight_layout()
    bins = numpy.linspace(cfg['etimemin'], cfg['etimemax'], 50)
    axapp.hist(app_data, bins, alpha=0.5, label='app')
    axapp.set_title('MG2 on CESM', fontsize=TITLE_SIZE)
    axapp.set_xlabel('Elapsed time (ms)', fontsize=LABEL_SIZE)
    axapp.set_ylabel('Frequency', fontsize=LABEL_SIZE)
    for tick in axapp.xaxis.get_major_ticks():
        tick.label.set_fontsize(TICKLABEL_SIZE) 
    for tick in axapp.yaxis.get_major_ticks():
        tick.label.set_fontsize(TICKLABEL_SIZE) 
    axapp.xaxis.set_major_formatter(ticks_x)
    #plt.legend(loc='upper right')

    bins = numpy.linspace(cfg['etimemin'], cfg['etimemax'], 50)
    axkernel.hist(kernel_data['etimes_kernel'], bins, alpha=0.5, label='kernel')
    axkernel.set_title('MG2 kernel', fontsize=TITLE_SIZE)
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


    app_norm_etimes = normalize_samples(app_data)
    app_nsamples = len(app_data)
    kernel_nsamples = len(kernel_data['etimes_kernel'])

    pdf = PdfPages('etime_mg2_stat_org.pdf')

    fig, axstat = plt.subplots(figsize=(8, 6))
    axstat.axis([0, 1, 1, 0])
    axstat.axis('off')
    axstat.text(0.1, 0.1, 'Statistics of two samples', fontsize=TITLE_SIZE, horizontalalignment='left')

    stat_lines = []

    minval_app = numpy.amin(app_data) 
    minval_kernel = numpy.amin(kernel_data['etimes_kernel']) 
    minval_diff = (minval_kernel - minval_app) / minval_app
    stat_lines.append( ('Minimum', minval_app, minval_kernel, minval_diff) ) # Minumum

    maxval_app = numpy.amax(app_data) 
    maxval_kernel = numpy.amax(kernel_data['etimes_kernel']) 
    maxval_diff = (maxval_kernel - maxval_app) / maxval_app
    stat_lines.append( ('Maximum', maxval_app, maxval_kernel, maxval_diff )) # Maximum

    median_app = numpy.median(app_data) 
    median_kernel = numpy.median(kernel_data['etimes_kernel']) 
    median_diff = (median_kernel - median_app) / median_app
    stat_lines.append( ('Median', median_app, median_kernel, median_diff )) # Maximum

    average_app = numpy.average(app_data) 
    average_kernel = numpy.average(kernel_data['etimes_kernel']) 
    average_diff = (average_kernel - average_app) / average_app
    stat_lines.append( ('Average', average_app, average_kernel, average_diff )) # Maximum

    mean_app = numpy.mean(app_data) 
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


    # ADJ

    kadj0_filepath = '%s/run_ys_30_0aM.txt'%cfg['mg2path']
    kadj0_data = cfg['kernels'][kadj0_filepath]
    #kadj20_filepath = '%s/run_ys_30_20M.txt'%cfg['mg2path']
    #kadj20_filepath = '%s/run_ys_30_20MB.txt'%cfg['mg2path']
    kadj20_filepath = '%s/run_ys_30_rand1M.txt'%cfg['mg2path']
    kadj20_data = cfg['kernels'][kadj20_filepath]

    pdf = PdfPages('etime_mg2_adj.pdf')

    fig, (axapp, axkernel) = plt.subplots(1, 2, figsize=(12,6))

    #fig.tight_layout()
    bins = numpy.linspace(cfg['etimemin'], cfg['etimemax'], 50)
    axapp.hist(kadj0_data['etimes_kernel'], bins, alpha=0.5, label='app')
    axapp.set_title('MG2 kernel\n(30 ranks, No cache pollution)', fontsize=TITLE_SIZE)
    axapp.set_xlabel('Elapsed time (ms)', fontsize=LABEL_SIZE)
    axapp.set_ylabel('Frequency', fontsize=LABEL_SIZE)
    for tick in axapp.xaxis.get_major_ticks():
        tick.label.set_fontsize(TICKLABEL_SIZE) 
    for tick in axapp.yaxis.get_major_ticks():
        tick.label.set_fontsize(TICKLABEL_SIZE) 
    axapp.xaxis.set_major_formatter(ticks_x)
    #plt.legend(loc='upper right')

    bins = numpy.linspace(cfg['etimemin'], cfg['etimemax'], 50)
    axkernel.hist(kadj20_data['etimes_kernel'], bins, alpha=0.5, label='kernel')
    axkernel.set_title('MG2 kernel\n(30 ranks, randomized cache pollution)', fontsize=TITLE_SIZE)
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


    kernel_nsamples = len(kadj0_data['etimes_kernel'])
    kernel_norm_etimes = normalize_samples(kadj0_data['etimes_kernel'], size=kernel_nsamples)

    pdf = PdfPages('etime_mg2_stat_adj.pdf')

    fig, axstat = plt.subplots(figsize=(8, 6))
    axstat.axis([0, 1, 1, 0])
    axstat.axis('off')
    axstat.text(0.1, 0.1, 'Statistics of two samples', fontsize=TITLE_SIZE, horizontalalignment='left')

    stat_lines = []

    minval_app = numpy.amin(app_data) 
    minval_kernel = numpy.amin(kadj0_data['etimes_kernel']) 
    minval_diff = (minval_kernel - minval_app) / minval_app
    stat_lines.append( ('Minimum', minval_app, minval_kernel, minval_diff) ) # Minumum

    maxval_app = numpy.amax(app_data) 
    maxval_kernel = numpy.amax(kadj0_data['etimes_kernel']) 
    maxval_diff = (maxval_kernel - maxval_app) / maxval_app
    stat_lines.append( ('Maximum', maxval_app, maxval_kernel, maxval_diff )) # Maximum

    median_app = numpy.median(app_data) 
    median_kernel = numpy.median(kadj0_data['etimes_kernel']) 
    median_diff = (median_kernel - median_app) / median_app
    stat_lines.append( ('Median', median_app, median_kernel, median_diff )) # Maximum

    average_app = numpy.average(app_data) 
    average_kernel = numpy.average(kadj0_data['etimes_kernel']) 
    average_diff = (average_kernel - average_app) / average_app
    stat_lines.append( ('Average', average_app, average_kernel, average_diff )) # Maximum

    mean_app = numpy.mean(app_data) 
    mean_kernel = numpy.mean(kadj0_data['etimes_kernel']) 
    mean_diff = (mean_kernel - mean_app) / mean_app
    stat_lines.append( ('Mean', mean_app, mean_kernel, mean_diff )) # Maximum

    std_app = numpy.std(app_norm_etimes) 
    std_kernel = numpy.std(kernel_norm_etimes) 
    std_diff = (std_kernel - std_app) / std_app
    stat_lines.append( ('SVar', std_app, std_kernel, std_diff )) # Maximum

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
    ##correlate = numpy.correlate(cfg['etimes_app'], kadj0_data['etimes_kernel']) 
    #correlate = numpy.correlate(app_norm_etimes, kernel_norm_etimes) 
    #axstat.text(0.1, yloc, 'Correlation: %f'%correlate[0], fontsize=TEXT_SIZE, horizontalalignment='left')

    pdf.savefig(fig)


    kernel_nsamples = len(kadj20_data['etimes_kernel'])
    kernel_norm_etimes = normalize_samples(kadj20_data['etimes_kernel'], size=kernel_nsamples)

    fig, axstat = plt.subplots(figsize=(8, 6))
    axstat.axis([0, 1, 1, 0])
    axstat.axis('off')
    axstat.text(0.1, 0.1, 'Statistics of two samples', fontsize=TITLE_SIZE, horizontalalignment='left')

    stat_lines = []

    minval_app = numpy.amin(app_data) 
    minval_kernel = numpy.amin(kadj20_data['etimes_kernel']) 
    minval_diff = (minval_kernel - minval_app) / minval_app
    stat_lines.append( ('Minimum', minval_app, minval_kernel, minval_diff) ) # Minumum

    maxval_app = numpy.amax(app_data) 
    maxval_kernel = numpy.amax(kadj20_data['etimes_kernel']) 
    maxval_diff = (maxval_kernel - maxval_app) / maxval_app
    stat_lines.append( ('Maximum', maxval_app, maxval_kernel, maxval_diff )) # Maximum

    median_app = numpy.median(app_data) 
    median_kernel = numpy.median(kadj20_data['etimes_kernel']) 
    median_diff = (median_kernel - median_app) / median_app
    stat_lines.append( ('Median', median_app, median_kernel, median_diff )) # Maximum

    average_app = numpy.average(app_data) 
    average_kernel = numpy.average(kadj20_data['etimes_kernel']) 
    average_diff = (average_kernel - average_app) / average_app
    stat_lines.append( ('Average', average_app, average_kernel, average_diff )) # Maximum

    mean_app = numpy.mean(app_data) 
    mean_kernel = numpy.mean(kadj20_data['etimes_kernel']) 
    mean_diff = (mean_kernel - mean_app) / mean_app
    stat_lines.append( ('Mean', mean_app, mean_kernel, mean_diff )) # Maximum

    std_app = numpy.std(app_norm_etimes) 
    std_kernel = numpy.std(kernel_norm_etimes) 
    std_diff = (std_kernel - std_app) / std_app
    stat_lines.append( ('SVar', std_app, std_kernel, std_diff )) # Maximum

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
    ##correlate = numpy.correlate(cfg['etimes_app'], kadj20_data['etimes_kernel']) 
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
