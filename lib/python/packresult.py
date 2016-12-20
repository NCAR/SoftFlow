
import os
import sys
import shutil

# result filename
JSONFILE = result.json

def cmd_init(workdir):
    filepath = os.path.join(workdir, JSONFILE)
    if os.path.exists(filepath):
        count = 1
        while os.path.exists('%s.%d'%(filepath, count))
            count += 1
        shutil.move(filepath, '%s.%d'%(filepath, count))





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
        result = cmd_init(workdir)
    else:
        print "Unknown command: %s"%command
        sys.exit(-1)

    return result

if __name__ == "__main__":
    main()
