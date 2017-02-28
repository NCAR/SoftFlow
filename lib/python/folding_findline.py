# dg_kernel plots

import os
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import csv
import sys

NE_SIZE = 128
TITLE_SIZE = 35 
TEXT_SIZE = 30 
MARKER_SIZE = 10
LINE_WIDTH = 5
colors = { idx:cname for idx, cname in enumerate(mcolors.cnames) }

eventname = 'L1_DCM'
callstacklevel = 7

FREQ_THRESHOLD = 0.02

ROOT = '/global/homes/g/grnydawn/trepo/temp/cylcworkspace/extrae_HSW/cgroup/folding/02242017_1353/codeline'

# read histogram file
def read_histogram(histofile):
    histodict = {}
    with open(histofile, 'rb') as f:
        reader = csv.reader(f, delimiter='\t')
        try:
            exclude_item = []
            for i, row in enumerate(reader):
                if len(row)<1: continue
                if i==0:
                    name = []
                    for j, item in enumerate(row[1:]):
                        if len(item)<1:
                            exclude_item += [ j ]
                            continue
                        name += [ item ]
                    histodict['Head'] = name
                else:
                    numval = []
                    for j, item in enumerate(row[1:]):
                        if j in exclude_item: continue
                        try:
                            numval += [ float(item) ]
                        except Exception as e:
                            if len(item)<1:
                                numval += [ 0.0 ]
                            else:
                                print e
                    histodict[row[0]] = numval
        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (histofile, reader.line_num, e))

    return histodict

def draw_histogram(xname, yval, title, xlabel, ylabel, filename, xrange=None):

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.set_title(title, fontsize=TITLE_SIZE)
    ax.set_xlabel(xlabel, fontsize=TEXT_SIZE)
    ax.set_ylabel(ylabel, fontsize=TEXT_SIZE)

    if xrange: XL = xrange
    else: XL = [0, len(xname)]

    ax.set_xticks(range(len(xname)))
    newname = []
    for i, xn in enumerate(xname):
        if i%1==0:
            newname += [ xn ]
        else:
            newname += [ "" ]
    ax.set_xticklabels(newname)

    xval = np.arange(len(xname))[XL[0]:XL[1]] 
    yval = yval[XL[0]:XL[1]] 

    YL = [0, max(yval)*1.5]
    ax.axis(XL + YL)

    gridlines = ax.get_xaxis().get_gridlines()
    for gl in gridlines:
        gl.set_visible(False)

    ax.grid(b=True, which='major', color='b', linestyle='-', linewidth=0.5)
    ax.grid(b=False, which='minor', color='#888888', linestyle='-',linewidth=0.5)
    ax.grid(True)

    for label in ax.xaxis.get_ticklabels(): label.set_fontsize(TEXT_SIZE)
    #for label in ax.xaxis.get_ticklabels(): label.set_fontsize(20)
    for label in ax.yaxis.get_ticklabels(): label.set_fontsize(TEXT_SIZE)

    fnamelist = list(set(filename))
    clist = []
    for fname in filename:
        color = colors[fnamelist.index(fname)]
        clist += [ color ]

    width = (XL[1]-XL[0])/float(len(xval)*2)
    histo  = ax.bar(xval-width/2, yval, width, color=clist)

    dummy_bars = []
    for i, fname in enumerate(fnamelist):
        dummy_bars += ax.bar([0], [1.E-16], width, color=colors[i])

    ax.legend(dummy_bars, fnamelist, loc=2)
    #plt.savefig("./dgomp.png")
    plt.show()       

peak1 = read_histogram('%s/%s_high_linelevel%d_region0.csv'%(ROOT, eventname, callstacklevel))
peak2 = read_histogram('%s/%s_high_linelevel%d_region1.csv'%(ROOT, eventname, callstacklevel))

peaks_avgsum = sum(peak1['Average']) + sum(peak2['Average'])
#print 'peaks_avgsum = ', peaks_avgsum

peaks_normavg = {}

for i, line in enumerate(peak1['Head']):
    if peaks_normavg.has_key(line):
        peaks_normavg[line] += peak1['Average'][i]
    else:
        peaks_normavg[line] = peak1['Average'][i]
for i, line in enumerate(peak2['Head']):
    if peaks_normavg.has_key(line):
        peaks_normavg[line] += peak2['Average'][i]
    else:
        peaks_normavg[line] = peak2['Average'][i]

#print 'peaks_normavg before = ', peaks_normavg.values()[:30]
for line in peaks_normavg.keys():
    peaks_normavg[line] = peaks_normavg[line]/peaks_avgsum
#print 'peaks_normavg after = ', peaks_normavg.values()[:30]


nonpeak1 = read_histogram('%s/%s_low_linelevel%d_region0.csv'%(ROOT, eventname, callstacklevel))
nonpeak2 = read_histogram('%s/%s_low_linelevel%d_region1.csv'%(ROOT, eventname, callstacklevel))

nonpeaks_avgsum = sum(nonpeak1['Average']) + sum(nonpeak2['Average'])

nonpeaks_normavg = {}

for i, line in enumerate(nonpeak1['Head']):
    if nonpeaks_normavg.has_key(line):
        nonpeaks_normavg[line] += nonpeak1['Average'][i]
    else:
        nonpeaks_normavg[line] = nonpeak1['Average'][i]
for i, line in enumerate(nonpeak2['Head']):
    if nonpeaks_normavg.has_key(line):
        nonpeaks_normavg[line] += nonpeak2['Average'][i]
    else:
        nonpeaks_normavg[line] = nonpeak2['Average'][i]

#print 'nonpeaks_normavg before = ', nonpeaks_normavg.values()[:30]
for line in nonpeaks_normavg.keys():
    nonpeaks_normavg[line] = nonpeaks_normavg[line]/nonpeaks_avgsum
#print 'nonpeaks_normavg after = ', nonpeaks_normavg.values()[:30]

#import pdb; pdb.set_trace()

result = {}
for line, bursts in peaks_normavg.iteritems():
    result[line] = bursts
for line, bursts in nonpeaks_normavg.iteritems():
    if result.has_key(line):
        result[line] -= bursts
    else:
        result[line] = -1.0*bursts

xlinenum = []
ybursts = []
filename = []
for line, bursts in result.iteritems():
    if bursts>FREQ_THRESHOLD:
        match = re.search(r'\s*(\d+)\s+\((.*)\)', line)
        if match:
            xlinenum += [ match.group(1) ]
            ybursts += [ float(bursts) ]
            matchfname = re.search(r'(\b\w+\.[cFf][\d]*\,)', match.group(2))
            if matchfname is None: 
                fname = 'Unresolved'
            else:
                fname = matchfname.group(1)[:-1]
            filename += [ fname ]
        
zipped = zip(xlinenum, ybursts, filename)
zipped.sort()
xlinenum, ybursts, filename = zip(*zipped)
#title = 'Frequent source lines in a region of interest' 
title = 'Frequent source lines at high %s regions in callstack level %d'%(eventname, callstacklevel)
xlabel = 'Sampled function line number'
ylabel = 'Normalized frequency'

draw_histogram(xlinenum, np.array(ybursts), title, xlabel, ylabel, filename)
