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

    rrtmgpath = '/glade/p/tdd/asap/kgen_data/cesm_rrtmg_lw'

    cfg['rrtmgpath'] = rrtmgpath 
    cfg['app'] = '%s/model.ini'%rrtmgpath 
    #cfg['runfiles'] = [ '%s/%s'%(rrtmgpath, etime) for etime in ( 'run_ys_1_0M.txt', 'run_ys_30_0M.txt', 'run_ys_30_random.txt' ) ]
    #cfg['runfiles'] = [ '%s/%s'%(rrtmgpath, etime) for etime in ( 'run_ys_1_0M.txt', 'run_ys_30_0M.txt', 'run_temp.txt' ) ]
    cfg['runfiles'] = [ '%s/%s'%(rrtmgpath, etime) for etime in ( 'run_ys_1_0M.txt', 'run_ys_30_0M.txt', 'run_ys_30_rand2M.txt' ) ]
    #cfg['runfiles'] = [ '%s/%s'%(rrtmgpath, etime) for etime in ( 'run_ys_1_0M.txt', 'run_ys_30_0aM.txt', 'run_ys_30_rand2M.txt' ) ]
    #cfg['runfiles'] = [ '%s/%s'%(rrtmgpath, etime) for etime in ( 'run_ys_1_0M.txt', 'run_ys_30_0M.txt', 'run_ys_22_random.txt' ) ]
    #cfg['runfiles'] = [ '%s/%s'%(rrtmgpath, etime) for etime in ( 'run_ys_1_0M.txt', 'run_ys_30_0M.txt', 'run_ys_18_0M.txt' ) ]
    #cfg['runfiles'] = [ '%s/%s'%(rrtmgpath, etime) for etime in ( 'run_ys_1_0M.txt', 'run_ys_30_0M.txt', 'run_ys_25_random.txt' ) ]
    #cfg['runfiles'] = [ '%s/%s'%(rrtmgpath, etime) for etime in ( 'run_ys_1_0M.txt', 'run_ys_30_0M.txt', 'run_ys_26_random.txt' ) ]
    cfg['minval'] = 0.003
    cfg['maxval'] = 0.011
    #cfg['minval'] = None
    #cfg['maxval'] = None

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

    cfg['etimemin'] = 0.003
    cfg['etimemax'] = 0.011

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
            #cfg['etimemin'] = min(cfg['etimemin'], etimeval)
            #cfg['etimemax'] = max(cfg['etimemax'], etimeval)

    except Exception as e:
        raise Exception('Please check the format of elapsedtime file: %s'%str(e))


    # read kernels
    cfg['kernels'] = {}
    for runfile in cfg['runfiles']:
        kernel_data = {}
        cfg['kernels'][os.path.basename(runfile)] = kernel_data
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
                    #cfg['etimemin'] = min(cfg['etimemin'], etimeval)
                    #cfg['etimemax'] = max(cfg['etimemax'], etimeval)

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
    kernel_data = cfg['kernels']['run_ys_1_0M.txt']

    pdf = PdfPages('etime_rrtmg.pdf')

    fig, ((axapp, axkernel), (axapp2, axkernel2)) = plt.subplots(2, 2, figsize=(12,12))

    #fig.tight_layout()
    plt.tight_layout(pad=9.0, w_pad=5.0, h_pad=10.0)

    bins = numpy.linspace(cfg['etimemin'], cfg['etimemax'], 50)
    axapp.hist(app_data, bins, alpha=0.5, label='app')
    axapp.set_title('RRTMG Longwave on CESM', fontsize=TITLE_SIZE)
    axapp.set_xlabel('Elapsed time (ms)\n(a)', fontsize=LABEL_SIZE)
    axapp.set_ylabel('Frequency', fontsize=LABEL_SIZE)
    for tick in axapp.xaxis.get_major_ticks():
        tick.label.set_fontsize(TICKLABEL_SIZE) 
    for tick in axapp.yaxis.get_major_ticks():
        tick.label.set_fontsize(TICKLABEL_SIZE) 
    axapp.xaxis.set_major_formatter(ticks_x)
    #plt.legend(loc='upper right')

    bins = numpy.linspace(cfg['etimemin'], cfg['etimemax'], 50)
    axkernel.hist(kernel_data['etimes_kernel'], bins, alpha=0.5, label='kernel')
    axkernel.set_title('RRTMG Longwave kernel', fontsize=TITLE_SIZE)
    axkernel.set_xlabel('Elapsed time (ms)\n(b)', fontsize=LABEL_SIZE)
    #axkernel.set_ylabel('Frequency', fontsize=LABEL_SIZE)
    for tick in axkernel.xaxis.get_major_ticks():
        tick.label.set_fontsize(TICKLABEL_SIZE) 
    for tick in axkernel.yaxis.get_major_ticks():
        tick.label.set_fontsize(TICKLABEL_SIZE) 
    axkernel.xaxis.set_major_formatter(ticks_x)
    #plt.legend(loc='upper right')
    #fig.autofmt_xdate()

    # ADJ

    #kadj0_filepath = '%s/run_ys_30_0M.txt'%cfg['rrtmgpath']
    kadj0_data = cfg['kernels'][os.path.basename(cfg['runfiles'][1])]
    #kadj20_filepath = '%s/run_ys_30_20M.txt'%cfg['rrtmgpath']
    #kadj20_filepath = '%s/run_ys_30_20MB.txt'%cfg['rrtmgpath']
    #kadj20_filepath = '%s/run_ys_30_random.txt'%cfg['rrtmgpath']
    #kadj20_filepath = '%s/run_ys_2_random.txt'%cfg['rrtmgpath']
    kadj20_data = cfg['kernels'][os.path.basename(cfg['runfiles'][2])]
    #kadj20_data = cfg['kernels'][kadj20_filepath]


    #fig.tight_layout()
    bins = numpy.linspace(cfg['etimemin'], cfg['etimemax'], 50)
    axapp2.hist(kadj0_data['etimes_kernel'], bins, alpha=0.5, label='app')
    #axapp2.set_title('RRTMG Longwave kernel\n(30 ranks, No cache pollution)', fontsize=TITLE_SIZE)
    #axapp2.set_title('RRTMG Longwave kernel\n(%s)'%os.path.basename(cfg['runfiles'][1]), fontsize=TITLE_SIZE)
    axapp2.set_title('RRTMG Longwave kernel\n(30 ranks, no cache pollution)', fontsize=TITLE_SIZE)
    axapp2.set_xlabel('Elapsed time (ms)\n(c)', fontsize=LABEL_SIZE)
    axapp2.set_ylabel('Frequency', fontsize=LABEL_SIZE)
    for tick in axapp2.xaxis.get_major_ticks():
        tick.label.set_fontsize(TICKLABEL_SIZE) 
    for tick in axapp2.yaxis.get_major_ticks():
        tick.label.set_fontsize(TICKLABEL_SIZE) 
    axapp2.xaxis.set_major_formatter(ticks_x)
    #plt.legend(loc='upper right')

    bins = numpy.linspace(cfg['etimemin'], cfg['etimemax'], 50)
    axkernel2.hist(kadj20_data['etimes_kernel'], bins, alpha=0.5, label='kernel')
    #axkernel2.set_title('RRTMG Longwave kernel\n(30 ranks, randomized cache pollution)', fontsize=TITLE_SIZE)
    #axkernel2.set_title('RRTMG Longwave kernel\n(%s)'%os.path.basename(cfg['runfiles'][2]), fontsize=TITLE_SIZE)
    axkernel2.set_title('RRTMG Longwave kernel\n(30 ranks, randomized cache pollution)', fontsize=TITLE_SIZE)
    axkernel2.set_xlabel('Elapsed time (ms)\n(d)', fontsize=LABEL_SIZE)
    #axkernel2.set_ylabel('Frequency', fontsize=LABEL_SIZE)
    for tick in axkernel2.xaxis.get_major_ticks():
        tick.label.set_fontsize(TICKLABEL_SIZE) 
    for tick in axkernel2.yaxis.get_major_ticks():
        tick.label.set_fontsize(TICKLABEL_SIZE) 
    axkernel2.xaxis.set_major_formatter(ticks_x)
    #plt.legend(loc='upper right')
    #fig.autofmt_xdate()
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
