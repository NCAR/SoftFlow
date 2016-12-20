#!/usr/bin/python

import os
import sys
import shutil
import json

# result filename
JSONFILE = "result.json"

def cmd_init(workdir, args):
    if len(args) == 0: 
        print "ERROR: job name is not given."
        return -1

    filepath = os.path.join(workdir, JSONFILE)
    if os.path.exists(filepath):
        count = 1
        while os.path.exists('%s.%d'%(filepath, count)):
            count += 1
        shutil.move(filepath, '%s.%d'%(filepath, count))

    jobdata = {}
    data = { 'jobs': { args[0]: jobdata } }

    with open(filepath, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)

    return 0

def cmd_pack(workdir, args):
    print "***********************************************************"
    print "Job result is saved in %s."%os.path.join(workdir, JSONFILE)
    print "***********************************************************"

def main():
    # directory, command type, arguments
    if len(sys.argv) < 3:
        print "Usage: %s <workdir> <command type> [argument(s)]"%sys.argv[0]
        sys.exit(-1)

    if not os.path.exists(sys.argv[1]):
        print "ERROR: %s does not exist."%sys.argv[1]
        sys.exit(-1)

    workdir = sys.argv[1]
    command = sys.argv[2]
    if len(sys.argv) > 3:
        args = sys.argv[3:]
    else:
        args = []

    result = 0

    if command == "init":
        result = cmd_init(workdir, args)
    elif command == "pack":
        result = cmd_pack(workdir, args)
    else:
        print "Unknown command: %s"%command
        sys.exit(-1)

    return result

if __name__ == "__main__":
    main()
