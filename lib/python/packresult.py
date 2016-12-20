#!/usr/bin/python

# NOTE
# - This script should be run under Cylc execution env.

import os
import sys
import shutil
import json
import subprocess
from datetime import datetime
from cStringIO import StringIO
from sfutil import openjson

JSONFILE = "result.json"

def _shcmd(cmd):
    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    return  out.strip()

def cmd_init(suitename, rundir, args):

    filepath = os.path.join(rundir, JSONFILE)
    if os.path.exists(filepath):
        count = 1
        while os.path.exists('%s.%d'%(filepath, count)):
            count += 1
        shutil.move(filepath, '%s.%d'%(filepath, count))

    jobdata = {}
    data = { suitename: jobdata }

    jobdata['begin'] = str(datetime.now())

    jobhost = {}
    jobdata['job-host'] = jobhost


    jobhost['node'] = os.environ['CYLC_SUITE_HOST']
    jobhost['cpu'] = _shcmd('cat /proc/cpuinfo | grep model | grep name | head -n 1 | cut -d ":" -f 2')

    with openjson(filepath, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)

    return 0

def cmd_pack(suitename, rundir, args):

    filepath = os.path.join(rundir, JSONFILE)

    with openjson(filepath, 'r') as data_file:
        data = json.load(data_file)

    data[os.environ['CYLC_SUITE_REG_NAME']]['end'] = str(datetime.now())

    print "***********************************************************"
    print "Job result is saved in %s."%os.path.join(rundir, JSONFILE)
    print "***********************************************************"

    return 0

def cmd_shell(suitename, rundir, args):

    filepath = os.path.join(rundir, JSONFILE)

    value = args[0]
    #print _shcmd(args[1:])

    with openjson(filepath, 'r') as data_file:
        data = json.load(data_file)

    if 'tasks' not in data[suitename]:
        tasks = {}
        data[suitename]['tasks'] = tasks
    else:
        tasks = data[suitename]['tasks']

    if os.environ['CYLC_TASK_ID'] not in tasks:
        taskid = {}
        tasks[os.environ['CYLC_TASK_ID']] = taskid
    else:
        taskid = tasks[os.environ['CYLC_TASK_ID']]

    taskid[value] = ret[0].strip()

    with openjson(filepath, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)

    return 0

def cmd_set(suitename, rundir, args):
    subcmd = args[0]
    namepath = args[1].split('##')
    value = ' '.join(args[2:])

    filepath = os.path.join(rundir, JSONFILE)
    
    with openjson(filepath, 'r') as data_file:    
        data = json.load(data_file)

    parent = data[os.environ['CYLC_SUITE_REG_NAME']]
    for name in namepath[:-1]:
        if name not in parent:
            newdict = {}
            parent[name] = newdict
            parent = newdict
        else:
            parent = parent[name]

    if subcmd == 'replace':
        parent[namepath[-1]] = value
    else:
        print "Unknown sub-command: %s"%args
        sys.exit(-1)
 
    with openjson(filepath, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)

    return 0
  
def cmd_outfile(suitename, rundir, args):
    print os.path.join(rundir, JSONFILE)
    return 0

def main():
    # directory, command type, arguments
    if len(sys.argv) < 2:
        print "Usage: %s <command type> [argument(s)]"%sys.argv[0]
        sys.exit(-1)

    rundir = os.environ['CYLC_SUITE_RUN_DIR']
    suitename = os.environ['CYLC_SUITE_REG_NAME']

    command = sys.argv[1]
    if len(sys.argv) > 2:
        args = sys.argv[2:]
    else:
        args = []

    result = 0

    if command in [ 'init', 'pack', 'shell', 'set', 'outfile']:
        result = eval('cmd_%s( suitename, rundir, args )'%command)
    else:
        print "Unknown command: %s %s"%(command, args)
        sys.exit(-1)

    return result

if __name__ == "__main__":
    sys.exit(main())
