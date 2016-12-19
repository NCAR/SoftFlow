#!/usr/bin/env python

import os
import sys
from scipy import stats
from ulparser import ULParser

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
    if len(sys.argv) < 3:
        print "Usage: %s <file1> <file2>"%sys.argv[0]
        sys.exit(-1)

    if not os.path.exists(sys.argv[1]):
        print "ERROR: %s does not exist."%sys.argv[1]
        sys.exit(-1)
        
    if not os.path.exists(sys.argv[2]):
        print "ERROR: %s does not exist."%sys.argv[2]
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

    # t-test
    for datafile, baseline in testdata[0].items():
        paired_sample = stats.ttest_rel(baseline, testdata[1][datafile])
        print "The t-statistic is %.3f and the p-value is %.3f." % paired_sample

    # report

if __name__ == "__main__":
    main()
