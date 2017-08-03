import sys

try:
    import configparser
except:
    import ConfigParser as configparser

try:
    from  matplotlib import pyplot as plt
    from  matplotlib import colors as mcolors
    from matplotlib.backends.backend_pdf import PdfPages

    colors = { idx:cname for idx, cname in enumerate(mcolors.cnames) }
except:
    print ('ERROR: matplotlib module is not loaded.')
    sys.exit(-1)

def main():

    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    cfg.read(sys.argv[1])

    mpi = {}
    omp = {}
    inv = {}

    fig, ax = plt.subplots(figsize=(8, 6))
    for opt in cfg.options('elapsedtime.elapsedtime'):
        ranknum, threadnum, invokenum = tuple( int(num) for num in opt.split() )
        start, stop = cfg.get('elapsedtime.elapsedtime', opt).split(',')
        diff = float(stop) - float(start)
        
        if ranknum not in mpi:
            mpi[ranknum] = []
        mpi[int(ranknum)].append(diff)

        if threadnum not in omp:
            omp[threadnum] = []
        omp[threadnum].append(diff)

        if invokenum not in inv:
            inv[invokenum] = []
        inv[invokenum].append(diff)

    for num, vals in omp.items():
        ax.scatter( [num] * len(vals), vals)
    
    plt.show()

if __name__ == "__main__":
    main()
