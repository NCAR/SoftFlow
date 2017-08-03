#!/usr/bin/python
'''Plotting script for Extrae folding results
'''

# TODO:
#absolute time
#split vertically
#meaningful event name
#only one of three repetted pattern

from __future__ import print_function

import os
import sys
import math
import glob
from argparse import ArgumentParser
from collections import OrderedDict
from csv import DictReader
from datetime import datetime

# Colormaps
'''
Accent, Accent_r, Blues, Blues_r, BrBG, BrBG_r, BuGn, BuGn_r, BuPu, BuPu_r, CMRmap, CMRmap_r, Dark2, Dark2_r, GnBu, GnBu_r, Greens, Greens_r, Greys, Greys_r, OrRd, OrRd_r, Oranges, Oranges_r, PRGn, PRGn_r, Paired, Paired_r, Pastel1, Pastel1_r, Pastel2, Pastel2_r, PiYG, PiYG_r, PuBu, PuBuGn, PuBuGn_r, PuBu_r, PuOr, PuOr_r, PuRd, PuRd_r, Purples, Purples_r, RdBu, RdBu_r, RdGy, RdGy_r, RdPu, RdPu_r, RdYlBu, RdYlBu_r, RdYlGn, RdYlGn_r, Reds, Reds_r, Set1, Set1_r, Set2, Set2_r, Set3, Set3_r, Spectral, Spectral_r, Wistia, Wistia_r, YlGn, YlGnBu, YlGnBu_r, YlGn_r, YlOrBr, YlOrBr_r, YlOrRd, YlOrRd_r, afmhot, afmhot_r, autumn, autumn_r, binary, binary_r, bone, bone_r, brg, brg_r, bwr, bwr_r, cool, cool_r, coolwarm, coolwarm_r, copper, copper_r, cubehelix, cubehelix_r, flag, flag_r, gist_earth, gist_earth_r, gist_gray, gist_gray_r, gist_heat, gist_heat_r, gist_ncar, gist_ncar_r, gist_rainbow, gist_rainbow_r, gist_stern, gist_stern_r, gist_yarg, gist_yarg_r, gnuplot, gnuplot2, gnuplot2_r,
gnuplot_r, gray, gray_r, hot, hot_r, hsv, hsv_r, inferno, inferno_r, jet, jet_r, magma, magma_r, nipy_spectral, nipy_spectral_r, ocean, ocean_r, pink, pink_r, plasma, plasma_r, prism, prism_r, rainbow, rainbow_r, seismic, seismic_r, spectral, spectral_r, spring, spring_r, summer, summer_r, terrain, terrain_r, viridis, viridis_r, winter, winter_r
'''

# named colors
'''
{0: u'indigo', 1: u'gold', 2: u'hotpink', 3: u'firebrick', 4: u'indianred', 5: u'sage', 6: u'yellow', 7: u'mistyrose', 8: u'darkolivegreen', 9: u'olive', 10: u'darkseagreen', 11: u'pink', 12: u'tomato', 13: u'lightcoral', 14: u'orangered', 15: u'navajowhite', 16: u'lime', 17: u'palegreen', 18: u'darkslategrey', 19: u'greenyellow', 20: u'burlywood', 21: u'seashell', 22: u'mediumspringgreen', 23: u'fuchsia', 24: u'papayawhip', 25: u'blanchedalmond', 26: u'chartreuse', 27: u'dimgray', 28: u'black', 29: u'peachpuff', 30: u'springgreen', 31: u'aquamarine', 32: u'white', 33: u'orange', 34: u'lightsalmon', 35: u'darkslategray', 36: u'brown', 37: u'ivory', 38: u'dodgerblue', 39: u'peru', 40: u'darkgrey', 41: u'lawngreen', 42: u'chocolate', 43: u'crimson', 44: u'forestgreen', 45: u'slateblue', 46: u'lightseagreen', 47: u'cyan', 48: u'mintcream', 49: u'silver', 50: u'antiquewhite', 51: u'mediumorchid', 52: u'skyblue', 53: u'gray', 54: u'darkturquoise', 55: u'goldenrod', 56: u'darkgreen', 57:
u'floralwhite', 58: u'darkviolet', 59: u'darkgray', 60: u'moccasin', 61: u'saddlebrown', 62: u'grey', 63: u'darkslateblue', 64: u'lightskyblue', 65: u'lightpink', 66: u'mediumvioletred', 67: u'slategrey', 68: u'red', 69: u'deeppink', 70: u'limegreen', 71: u'darkmagenta', 72: u'palegoldenrod', 73: u'plum', 74: u'turquoise', 75: u'lightgrey', 76: u'lightgoldenrodyellow', 77: u'darkgoldenrod', 78: u'lavender', 79: u'maroon', 80: u'yellowgreen', 81: u'sandybrown', 82: u'thistle', 83: u'violet', 84: u'navy', 85: u'magenta', 86: u'dimgrey', 87: u'tan', 88: u'rosybrown', 89: u'olivedrab', 90: u'blue', 91: u'lightblue', 92: u'ghostwhite', 93: u'honeydew', 94: u'cornflowerblue', 95: u'linen', 96: u'darkblue', 97: u'powderblue', 98: u'seagreen', 99: u'darkkhaki', 100: u'snow', 101: u'sienna', 102: u'mediumblue', 103: u'royalblue', 104: u'lightcyan', 105: u'green', 106: u'mediumpurple', 107: u'midnightblue', 108: u'cornsilk', 109: u'paleturquoise', 110: u'bisque', 111: u'slategray', 112:
u'darkcyan', 113: u'khaki', 114: u'wheat', 115: u'teal', 116: u'darkorchid', 117: u'deepskyblue', 118: u'salmon', 119: u'darkred', 120: u'steelblue', 121: u'palevioletred', 122: u'lightslategray', 123: u'aliceblue', 124: u'lightslategrey', 125: u'lightgreen', 126: u'orchid', 127: u'gainsboro', 128: u'mediumseagreen', 129: u'lightgray', 130: u'mediumturquoise', 131: u'darksage', 132: u'lemonchiffon', 133: u'cadetblue', 134: u'lightyellow', 135: u'lavenderblush', 136: u'coral', 137: u'purple', 138: u'aqua', 139: u'lightsage', 140: u'whitesmoke', 141: u'mediumslateblue', 142: u'darkorange', 143: u'mediumaquamarine', 144: u'darksalmon', 145: u'beige', 146: u'blueviolet', 147: u'azure', 148: u'lightsteelblue', 149: u'oldlace'}
'''

try:
    from  matplotlib import pyplot as plt
    from  matplotlib import colors as mcolors
    from matplotlib.backends.backend_pdf import PdfPages

    #plt.rcParams['image.cmap'] = 'Accent'
    #colors = { idx:cname for idx, cname in enumerate(mcolors.cnames) }
    #colors = { 0:'r', 1:'b', 2:'royalblue', 3:'palevioletred', 4:'chartreuse' }
    colors = { 0:'r', 1:'b', 2:'lightgrey', 3:'grey', 4:'darkgrey' }
    pdf = PdfPages('exfill_report.pdf')
except Exception as e:
    print ('ERROR: matplotlib module is not loaded: %s'%str(e))
    sys.exit(-1)

FIELDNAMES = [ 'region', 'group', 'counter', 'xval', 'yval' ]
TITLE_SIZE = 24
SUBTITLE_SIZE = 18
TEXT_SIZE = 14
LABEL_SIZE = 18
LINEWIDTH = 3

# Folded sampling caller level event range: 630000000 - 630000015
#CALLER_EVENTS = tuple( str(event) for event in range(630000000,(630000015+1)) )
CALLER_EVENTS = tuple( str(event) for event in range(630000000,(630000005+1)) )
#CALLER_EVENTS = tuple( '630000005' )

papi_descs = {
'PAPI_RES_STL' : 'Stalled resource cycles',
'PAPI_STL_ICY' : 'No instrurction issue',
'PAPI_TOT_INS' : 'Instructions completed',
'PAPI_BR_TKN' : 'Conditional branch taken',
'PAPI_BR_MSP' : 'Conditional branch mispredicted',
'PAPI_BR_UCN' : 'Unconditional branch',
'PAPI_BR_INS' : 'Branches',
'PAPI_BR_CN' : 'Conditional branch',
'PAPI_TLB_DM' : 'Data TLB misses',
'PAPI_VEC_DP' : 'Double precision vector instructions',
'PAPI_L3_DCR' : 'L3 data cache reads',
'PAPI_L3_DCW' : 'L3 data cache writes',
'PAPI_L2_TCH' : 'L2 cache hits',
'PAPI_L2_DCR' : 'L2 data cache reads',
'PAPI_L2_DCW' : 'L2 data cache writes',
'PAPI_L2_TCA' : 'L2 cache accesses',
'PAPI_L2_TCM' : 'L2 cache misses',
'PAPI_L2_LDM' : 'L2 load misses',
'PAPI_L1_ICH' : 'L1 instruction cache hits',
'PAPI_L1_ICA' : 'L1 instruction cache accesses',
'PAPI_L1_DCA' : 'L1 data cache accesses',
'PAPI_LD_INS' : 'Loads',
'PAPI_LST_INS' : 'Loads and stores completed',
'PAPI_L1_DCM' : 'L1 data cache misses',
'PAPI_L1_ICM' : 'L1 instruction cache misses',
'PAPI_L1_TCM' : 'L1 cache misses',
'PAPI_L1_LDM' : 'L1 load misses',
'PAPI_L1_STM' : 'L1 store misses',
'OFFCORE_RESPONSE0:MCDRAM_NEAR' : 'Responses from MCDRAM near',
'OFFCORE_RESPONSE0:MCDRAM_FAR' : 'Responses from MCDRAM far or other L2 cache',
'UOPS_RETIRED:PACKED_SIMD' : 'All vector instructions'
}

funcnamemap = { 'compute_and_apply_rhs': 'compute_and_apply_rhs', 
    'euler_step': 'dynamics and tracers',
    'advance_hypervis_dp': 'dissipation'
}

hatchs = [ '\\\\', '-', '//' ]

cfg = OrderedDict()

def parse_args():

    # argument parsing
    parser = ArgumentParser(description='Plotting Extrae folding results')
    parser.add_argument('folddirs', metavar='folding-dir', type=str, nargs='+', help='Directory containing folded Extrae raw data')
    parser.add_argument('-e', '--event', dest='event', type=str, action='append', default=None, help='Events to use (default: all events)')
    parser.add_argument('-f', '--function', dest='function', type=str, action='append', default=None, help='Functions to use (default: no function)')
    parser.add_argument('-t', '--time', dest='etime', action='store_true', default=False, help='Add elapsed time in plot (default: No)')
    parser.add_argument('--exclude-per-ins', dest='exclude_per_ins', action='store_true', default=False, help='Exclude per_ins events (default: No)')
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

     # exclude per_ins events
    cfg['exclude_per_ins'] = args.exclude_per_ins
 
    # folding dirs
    folddirs = []
    cfg['folddirs'] = folddirs

    flags = OrderedDict()
    cfg['flags'] = flags

    # prvfiles
    prvfiles = OrderedDict()
    cfg['prvfiles'] = prvfiles

    fillfuncs = []
    if args.function:
        for funcs in args.function:
            fillfuncs.extend(funcs.split(','))
    cfg['fillfuncs'] = fillfuncs

    if args.etime:
        flags['etime'] = args.etime

     # app name
    cfg['appnames'] = OrderedDict()

    # csvfiles
    csvfiles = OrderedDict()
    cfg['csvfiles'] = csvfiles

    # elapsed time
    etimes = OrderedDict()
    cfg['etimes'] = etimes

    # system
    systems = []
    cfg['systems'] = systems

    for folddirpair in args.folddirs:
        fsplit = folddirpair.split(':')
        if len(fsplit) == 2:
            cfg['appnames'][os.path.abspath(fsplit[0])] = fsplit[1]
            folddir = fsplit[0]
        elif len(fsplit) == 1:
            folddir = fsplit[0]
        else:
            raise Exception('Wrong format of folding data path: %s'%folddirpair)

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
            elif pathname.endswith('codeblocks.fused.folded.pcf'):
                if absfolddir not in prvfiles:
                    prvfiles[absfolddir] = [ os.path.abspath(pathname), None ]
                else:
                    prvfiles[absfolddir][0] = os.path.abspath(pathname)
            elif pathname.endswith('codeblocks.fused.folded.prv'):
                if absfolddir not in prvfiles:
                    prvfiles[absfolddir] = [ None, os.path.abspath(pathname) ]
                else:
                    prvfiles[absfolddir][1] = os.path.abspath(pathname)
       
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
                elif not ( isinstance(cfg['events'], bool) and cfg['events'] ):
                    continue
                elif cfg['exclude_per_ins'] and row['counter'].endswith('per_ins'):
                    continue

                # counter
                if row['counter'] not in csvdata:
                    counter = OrderedDict()
                    csvdata[ row['counter'] ] = counter
                else:
                    counter = csvdata[ row['counter'] ]

                # region
                if absfolddir in cfg['appnames']:
                    region_name = cfg['appnames'][absfolddir]
                else:
                    region_name = row['region']
                if region_name not in counter:
                    region = OrderedDict()
                    counter[ region_name ] = region
                else:
                    region = counter[ region_name ]

                if absfolddir not in regions:
                    regions[absfolddir] = region_name

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
                elif absfolddir not in cfg['appnames']:
                    import pdb; pdb.set_trace()
                    raise Exception('Dupulicated values: %s from %s.'%(str(row), csvfile))


def read_pcf(pcffile):

    funcmap = {} # num: name

    (PREREGION, FOLDED_EVENTS, FUNCMAP, POSTREGION) = range(4)

    with open(pcffile, 'r') as pcf:
        stage = PREREGION
        for row in pcf:
            if stage == PREREGION:
                if row.startswith('0 630000000'):
                    stage = FOLDED_EVENTS
            elif stage == FOLDED_EVENTS:
                if row.startswith('VALUES'):
                    stage = FUNCMAP
            elif stage == FUNCMAP:
                if len(row.strip()) == 0:
                    stage = POSTREGION
                else:
                    m = row.split()
                    funcnum = m[0]
                    if len(m) == 2:
                        funcname = m[1]
                    elif len(m) == 3:
                        funcname = m[2][1:-1]
                    
                    for fillfunc in cfg['fillfuncs']:
                        if funcname.endswith(fillfunc) or funcname.endswith(fillfunc + '_'):
                            funcmap[funcnum] = fillfunc
                            break

            elif stage == POSTREGION:
                break
    return funcmap

def read_prv(prvfile, funcnums, size):

    def build_func(begin, end, s):
        def calcindex(t):
            return int(1.0 * (t - begin) * (s - 1) / (end - begin))            
        return calcindex

    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    funcdata = {}
    for funcnum in funcnums:
        funcdata[funcnum] = [ 0 for _ in range(size) ]

    (PREREGION, BEGIN_TIME, DATA, POSTREGION) = range(4)

    tbegin = None
    calc = None

    with open(prvfile, 'r') as prv:
        stage = PREREGION
        for row in prv:
            rsplit = row.split(':')
            if stage == PREREGION:
                if len(rsplit) >= 8 and rsplit[6] == '600000001' and rsplit[7] == '1':
                    stage = BEGIN_TIME
                    tbegin = int(rsplit[5])
            elif stage == BEGIN_TIME:
                if len(rsplit) >= 8 and rsplit[6] == '600000001' and rsplit[7] == '0':
                    stage = DATA
                    tend = int(rsplit[5])
                    calc = build_func(tbegin, tend, size)
            elif stage == DATA:
                if len(rsplit) >= 8:
                    if rsplit[6] == '600000002':
                        stage = POSTREGION
                    else:
                        for event, value in chunks(rsplit[6:], 2):
                            if event in CALLER_EVENTS:
                                if value in funcnums:
                                    funcdata[value][calc(int(rsplit[5]))] = 1
            elif stage == POSTREGION:
                break

    return funcdata

def gen_masks():
    # per every functions specfied
    # generate mask arrays of True values
    # - read all folded sampled function to see the specified function exists and mark per each x-axis
    # - apply filter(integration)
    # - apply threashold to generate mask

    # constants
    WINSIZE = 15
    winceil = int(math.ceil(WINSIZE/2))
    winfloor = int(math.floor(WINSIZE/2))
    THRESHOLD = winceil

    # read data
    prvdata = {}
    cfg['prvdata'] = prvdata
    for absfolddir, (pcffile, prvfile) in cfg['prvfiles'].items():
        prvdata[absfolddir] = { 'funcmap': None, 'funclist': None, 'funcmask': {} }
        prvdata[absfolddir]['funcmap'] = read_pcf(pcffile)
        prvdata[absfolddir]['funclist'] = read_prv(prvfile, prvdata[absfolddir]['funcmap'].keys(), 999)

        funcmask = {}
        prvdata[absfolddir]['funcmask'] = funcmask
        for funcid, funcname in prvdata[absfolddir]['funcmap'].items():
            funcmask[funcname] = []
            l = prvdata[absfolddir]['funclist'][funcid]
            size = len(l)
            for idx in range(size):
                value = sum(l[ max(idx-winfloor, 0) : min(idx+winfloor, size)])  
                funcmask[funcname].append(True if value >= THRESHOLD else False)

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
        line = '%s (%s ms): %s'%(cfg['regions'][folddir], cfg['etimes'][folddir], folddir)
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
    for cnt in cfg['csvdata'].keys():
        if cnt.endswith('_per_ins') and cnt[:-8] not in counters:
            counters.append(cnt[:-8])

    listcnts = []
    for counter in counters:
        listcnts.append(counter)
        strcnts = ', '.join(listcnts)
        if len(strcnts) < 45: continue
        yloc += 0.05
        if yloc > 0.9:
            ax.axis('off')
            fig.tight_layout()
            pdf.savefig(fig)

            fig, ax = plt.subplots(figsize=(8, 6))
            ax.axis([0, 1, 1, 0])
            yloc = 0.1
          
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

        maxval = 0
        plotdata = OrderedDict()
        for region, vals in regions.items():
            plotdata[region] = (vals.keys(), vals.values())
            maxval = max(maxval, max(plotdata[region][1]))

        ax.text(0.5, 0.97, papi_descs.get(counter, ''), fontsize=SUBTITLE_SIZE, \
            horizontalalignment='center', verticalalignment='center')

        #ax.text(-0.1, 0.5, papi_descs.get(counter, ''), fontsize=LABEL_SIZE, \
        #    horizontalalignment='center', verticalalignment='center', rotation=90)

        ax.axis('off')
 
        func_labels = {}
        nplots = len(plotdata) 

        #axplot = fig.add_axes([0.15, 0.1, 0.8, 0.7])
        left = 0.15
        width = 0.8
        hdelta = 0.7 / nplots

        for idx, (region, (_xvals, yvals)) in enumerate(plotdata.items()):

            bottom = 0.1 + idx * hdelta

            axplot = fig.add_axes([left, bottom, width, hdelta*0.8])

            axplot.grid(color='lightgrey', linestyle='--', linewidth=1)
            axplot.set_axisbelow(True)

            axplot.set_title('%s (%s msec)'%(region, cfg['etimes'][cfg['folddirs'][idx]]), position=(0.5, 0.8))

            H = max(0.001, maxval*1.3)
            etime = float(cfg['etimes'][cfg['folddirs'][idx]])
            axplot.axis([0, etime, 0, H])

            if idx == 0:
                axplot.set_xlabel('elapsed time (msec)')

            if counter.find('per_ins') > 0:
                axplot.set_ylabel('events / instruction')
            else:
                axplot.set_ylabel('# events ( $\mathregular{10^{6}}$ )')

                xvals = [x*etime for x in _xvals]

                for absfolddir, regionname in cfg['regions'].items():
                    if regionname == region:
                        for cidx, (funcname, mask) in enumerate(cfg['prvdata'][absfolddir]['funcmask'].items()):
                            fplot = axplot.fill_between(xvals, yvals, where=mask, color=colors[cidx+2], hatch=hatchs[cidx])
                            if funcnamemap[funcname] not in func_labels:
                                func_labels[funcnamemap[funcname]] = fplot

                #plot = axplot.plot(xvals, yvals, color=colors[idx], linewidth=LINEWIDTH)
                plot = axplot.plot(xvals, yvals, color='darkslategrey', linewidth=LINEWIDTH)

                #if cfg['flags'].get('etime', False):
                #    labels.append('%s (%s ms)'%(region, cfg['etimes'][cfg['folddirs'][idx]]))
                #else:
                #    labels.append(region)

        #plt.legend(funcs, labels, loc=9)
        #plt.legend(funcs, labels, bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode="expand", borderaxespad=0.)
        funcs = []
        labels = []
        for l in sorted(func_labels.keys()):
            labels.append(l)
            funcs.append(func_labels[l])
        plt.legend(funcs, labels, bbox_to_anchor=(0., 1.02, 1., .204), loc=3, ncol=3, mode="expand", borderaxespad=0.)

        #fig.tight_layout()

        pdf.savefig(fig)

        plt.close()

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

    # generate masking data
    gen_masks()

    # generate a report
    gen_report()

if __name__ == '__main__':
    sys.exit(main())
