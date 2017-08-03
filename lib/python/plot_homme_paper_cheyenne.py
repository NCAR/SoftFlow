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
    import matplotlib.gridspec as gridspec

    #plt.rcParams['image.cmap'] = 'Accent'
    #colors = { idx:cname for idx, cname in enumerate(mcolors.cnames) }
    #colors = { 0:'r', 1:'b', 2:'royalblue', 3:'palevioletred', 4:'chartreuse' }
    colors = { 0:'r', 1:'b', 2:'lightgrey', 3:'grey', 4:'darkgrey' }
    pdf = PdfPages('exfill_report.pdf')
except Exception as e:
    print ('ERROR: matplotlib module is not loaded: %s'%str(e))
    sys.exit(-1)

FIELDNAMES = [ 'region', 'group', 'counter', 'xval', 'yval' ]
TITLE_SIZE = 18
SUBTITLE_SIZE = 12
TEXT_SIZE = 12
LABEL_SIZE = 10
LINEWIDTH = 1

# Folded sampling caller level event range: 630000000 - 630000015
#CALLER_EVENTS = tuple( str(event) for event in range(630000000,(630000015+1)) )
CALLER_EVENTS = tuple( str(event) for event in range(630000000,(630000005+1)) )
#CALLER_EVENTS = tuple( '630000005' )

papi_descs = {
'PAPI_RES_STL' : 'Stalled resource cycles',
'PAPI_STL_ICY' : 'No instrurction issue',
'PAPI_TOT_INS' : 'Instructions completed',
'PAPI_BR_TKN' : 'Conditional branch taken',
'PAPI_BR_MSP' : 'Conditional branch mspredictd',
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
'OFFCORE_RESPONSE0:MCDRAM_NEAR' : 'MCDRAM near',
'OFFCORE_RESPONSE0:MCDRAM_FAR' : 'MCDRAM far or other L2 cache',
'UOPS_RETIRED:PACKED_SIMD' : 'All vector instructions'
}

funcnamemap = { 'compute_and_apply_rhs': 'compute_and_apply_rhs', 
    'euler_step': 'dynamics and tracers',
    'advance_hypervis_dp': 'dissipation'
}

#hatchs = [ '\\\\', '-', '//' ]
hatchs = [ '\\\\', '++', '//' ]

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

def gen_plotpages():

    NROW = 2
    NCOL = 3

    # KNL
    #selected_counters = ( ( 'PAPI_L1_DCA', 'PAPI_L1_DCM' ), ( 'PAPI_L2_TCA', 'PAPI_L2_TCM' ), ( 'OFFCORE_RESPONSE0:MCDRAM_NEAR', 'OFFCORE_RESPONSE0:MCDRAM_FAR' ) )

    # BDW
    selected_counters = ( ( 'PAPI_L1_LDM', 'PAPI_L1_STM' ), ( 'PAPI_L2_DCR', 'PAPI_L2_DCW' ), ( 'PAPI_L3_DCR', 'PAPI_L3_DCW' ) )

    fig = plt.figure(figsize=(12, 7))
    #fig.suptitle('HOMME Cache Behavior (perfTestWACCM, ne=8) on Cheyenne', fontsize=TITLE_SIZE, fontweight='bold', y=1.0)

    outer = gridspec.GridSpec(NROW, NCOL, wspace=0.2, hspace=0.3)

    funcs = []
    labels = []

    fl = {}

    for row in range(NROW):

        plt.figtext( 0.075, 0.75 - row*0.4, '# events ($\mathregular{10^{6}}$)', fontsize=LABEL_SIZE, rotation='vertical' )

        for col in range(NCOL):

            inner = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=outer[row, col], wspace=0.1, hspace=0.3)

            counter = selected_counters[col][row]

            regions = cfg['csvdata'][counter]

            maxval = 0
            plotdata = OrderedDict()
            for region, vals in regions.items():
                plotdata[region] = (vals.keys(), vals.values())
                maxval = max(maxval, max(plotdata[region][1]))

            #import pdb; pdb.set_trace()

            for idx, (region, (_xvals, yvals)) in enumerate(reversed(sorted(plotdata.items()))):

                ax = plt.Subplot(fig, inner[idx])

                if region == 'original': # original
                    ch = chr(ord('a') + row + col*2)
                    ax.set_title( '%s (%s)'%(papi_descs.get(counter, ''), ch), fontsize=SUBTITLE_SIZE, horizontalalignment='center', verticalalignment='center' )
                else:
                    if row == 1:
                        ax.set_xlabel('elapsed time (msec)', fontsize=LABEL_SIZE)

                #if col == 0:
                #    ax.set_ylabel('# events ($\mathregular{10^{6}}$)', fontsize=LABEL_SIZE)

                xvals = []

                for absfolddir, regionname in cfg['regions'].items():
                    if regionname == region:
                        H = max(0.001, maxval*1.3)
                        etime = float(cfg['etimes'][absfolddir])
                        ax.axis([0, etime, 0, H])
                        xvals = [x*etime for x in _xvals]
                        t = ax.text(etime*0.5, H*0.85, '%s (%s msec)'%(region, cfg['etimes'][absfolddir]), ha='center')
                        break

                for coloridx, (funcname, mask) in enumerate(cfg['prvdata'][absfolddir]['funcmask'].items()):
                    fplot = ax.fill_between(xvals, yvals, where=mask, color=colors[coloridx+2], hatch=hatchs[coloridx])
                    if funcnamemap[funcname] not in fl:
                        fl[funcnamemap[funcname]] = fplot

                plot = ax.plot(xvals, yvals, color='darkslategrey', linewidth=LINEWIDTH)

                fig.add_subplot(ax)

    funcs = []
    labels = []
    for label in sorted(fl.keys()):
        labels.append(label)
        funcs.append(fl[label])

    fig.legend(funcs, labels, loc='lower center', ncol=3, borderaxespad=-0.5, frameon=False, fontsize=SUBTITLE_SIZE)

    #fig.show()
    plt.savefig('exfill_report_Cheyenne.png', bbox_inches='tight', format='png', dpi=600)
    pdf.savefig(fig, bbox_inches='tight')
    pdf.close()



def main():

    # argument parsing
    parse_args()

    # read folding data
    read_data()

    # generate masking data
    gen_masks()

    # plot pages
    gen_plotpages()

if __name__ == '__main__':
    sys.exit(main())
