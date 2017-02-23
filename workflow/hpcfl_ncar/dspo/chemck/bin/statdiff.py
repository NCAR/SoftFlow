#!/usr/bin/env python

import os
import sys
import json
from scipy import stats
from ulparser import ULParser
from sfutil import openjson
import random

logspecxml = """<?xml version="1.0"?>
<Log>
    <RepeatTest begin="JOB SCRIPT STARTING" end="JOB SCRIPT EXITING.+" >
        <Against begin="Verification against '(?P<datafile>.+)' " end="__Against__ ||imp_sol summary: # ranks" >
            <TimePerCall line="Time per call \(usec\):\s+(?P<timepercall>[\d\.]+)" />
            <Remainder line=".+" />
        </Against>
        <Remainder/>
    </RepeatTest>
</Log>
"""

def main():
    if len(sys.argv) < 4:
        print "Usage: %s <file1> <file2> <CPU type> [json filepath] [suite name]"%sys.argv[0]
        sys.exit(-1)

    if not os.path.exists(sys.argv[1]):
        print "ERROR: %s does not exist."%sys.argv[1]
        sys.exit(-1)
        
    if not os.path.exists(sys.argv[2]):
        print "ERROR: %s does not exist."%sys.argv[2]
        sys.exit(-1)

    if sys.argv[3] not in ['KNL', 'HSW', 'SNB']:
        print "ERROR: Unknown CPU type: %s"%sys.argv[3]
        sys.exit(-1)
   
    testdata = [{}, {}] 
    for idx in range(2):
        # parse files
        parser = ULParser(logspecxml.strip(), sys.argv[idx+1])
     
        # collect data
        for node, depth in parser.walk():
            if node.__class__.__name__ == 'Against':
                datafile = node.datafile[1:-1]
                if datafile not in testdata[idx]:
                    testdata[idx][datafile] = []
                for item in node.content:
                    if item.__class__.__name__ == 'TimePerCall':
                        testdata[idx][datafile].append(float(item.timepercall))
                        break


    blist = []
    flist = []
    for datafile, baseline in testdata[0].items():
        blist.extend(baseline)
        flist.extend(testdata[1][datafile])
    random.shuffle(blist)
    random.shuffle(flist)
    t, p = stats.ttest_rel(blist, flist)
    print "The t-statistic is %.3f and the p-value is %.3f." % (t, p)
    ttests = [abs(float(t)), float(p)]

#    for datafile, baseline in testdata[0].items():
#        t, p = stats.ttest_rel(baseline, testdata[1][datafile])
#        ttests.append([float(t), float(p)])
#        print "The t-statistic is %.3f and the p-value is %.3f." % (t, p)

    if len(sys.argv) >= 6:
        with openjson(sys.argv[4], 'r') as jsonfile:
            data = json.load(jsonfile)

        jobdata = data[sys.argv[5]]
        if sys.argv[3] not in jobdata:
            cpudata = {}
            jobdata[sys.argv[3]] = cpudata
        else:
            cpudata = jobdata[sys.argv[3]]
            
        cpudata['timepercall'] = testdata
        cpudata['t-tests'] = ttests

        with openjson(sys.argv[4], 'w') as jsonfile:
            json.dump(data, jsonfile, indent=4, sort_keys=True)

if __name__ == "__main__":
    main()
