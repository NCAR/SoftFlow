#!/bin/sh

# use -b option to exit after the build
# use -f option to force a new build
# use -u option to update executable

#BSUB -J cam-test
#BSUB -q premium
#BSUB -P STDD0002
#BSUB -W 12:00
#BSUB -n 16
#BSUB -R "span[ptile=16]"
#BSUB -o f19c5aqrpportm-1d.out%J
#BSUB -x
#BSUB -a poe

ntasks=16

#=====================================================================================================
# Machine environment

ulimit -c unlimited
export OMP_STACKSIZE=256M

# Use intel compilers (default) and use the compiler wrapper scripts
fc_type=intel
#fc_type=pgi
compiler="-fc mpif90 -cc mpicc -fc_type $fc_type"
source /glade/apps/opt/lmod/lmod/init/bash
if [ $fc_type = intel ]; then
    module swap intel intel/15.0.3
    module load mkl
else
    module swap intel $fc_type
fi
module load cmake/3.0.2
module load perlmods
module list

# MPI Environment
#export MP_LABELIO=yes
#export MP_INFOLEVEL=2
export MP_SHARED_MEMORY=yes
export MP_EUILIB=us
export MP_MPILIB=mpich2
export MP_STDOUTMODE=unordered
export MP_RC_USE_LMC=yes
export MP_EUIDEVELOP=min

#=====================================================================================================

# number of concurrent make tasks
nj=8

echo ' '
echo '---------------------------------------------------------------------------------'
date
hostname
uname -a
echo '==RUN ENVIRONMENT================================================================'
printenv | sort
echo ' '

while getopts ":bfu" opt; do
    case $opt in
	b  ) b=1 ;;
	f  ) f=1 ;;
	u  ) u=1 ;;
	\? ) echo "usage: $0 [-b] [-f] [-u]"
	     exit 1
    esac
done

# Root directory of CAM data distribution
export CSMDATA=/glade/p/cesmdata/cseg/inputdata

# Root directory of CAM distribution and the corresponding source ID
#cam_root=/glade/p/work/eaton/cam-src/rrtmgp14_cam5_4_48
#cam_root=/glade/u/home/youngsun/apps/port/rrtmgp14_cam5_4_48
cam_root=${CYLC_CAM_ROOT}
sid=${cam_root##/*/}

#wrkdir=/glade/scratch/eaton/$sid
#wrkdir=/glade/scratch/youngsun/cylcworkdir/port
wrkdir=${CYLC_WRKDIR}
cfgdir=$cam_root/components/cam/bld
logdir=`pwd`

#=========================================================================================================

echo ""
echo "----------------------------------------------------------------------"
cfgid=f19c5aqrpportm_${fc_type}
tstid=1d
case=${cfgid}_$tstid
echo "configID=$cfgid   test=$tstid"
echo "----------------------------------------------------------------------"

blddir=$wrkdir/${cfgid}_bld
rundir=$wrkdir/$case
logfile=$logdir/${case}_log.$$

mkdir -p $rundir                || exit 1
mkdir -p $blddir                || exit 1

cd $blddir
if [ "$u" = "1" ]; then
    echo "updating CAM ..."
    rm -f Depends
    gmake -j $nj >> MAKE.out 2>&1      || { echo "FAILURE-- see $blddir/MAKE.out"; exit 1; }
elif [ ! -x $blddir/cam ] || [ "$f" = "1" ]; then
    rm -rf *
    echo "configuring CAM in $blddir ..."
    $cfgdir/configure $compiler -dyn fv -hgrid 1.9x2.5 -phys cam5 -ocn aquaplanet -rad rrtmgp -offline_drv rad \
            -ntasks $ntasks -nosmp  || exit 1
    echo "building CAM: log in $blddir/MAKE.out ..."
    time gmake -j $nj > MAKE.out 2>&1      || { echo "FAILURE-- see $blddir/MAKE.out"; exit 1; }
fi

if [ -z "$b" ]; then

    cd $rundir

    runcmd="mpirun.lsf"

    rad_driving_data=/glade/scratch_old/eaton/rrtmgp12_cam5_4_48/f19c5aqh_intel_radgen-1d/f19c5aqh_intel_radgen-1d.cam.h1.0000-01-01-00000.nc

    #     stop_option='ndays' stop_n=1 restart_option='none'
    echo "building namelists for control run"
    $cfgdir/build-namelist -s -case $case -config $blddir/config_cache.xml \
	-ignore_ic_date \
	-namelist "&atm_in start_type='startup' start_ymd=101
         stop_option='nsteps' stop_n=24 restart_option='none'
         rrtmgp_iradsw=1 rrtmgp_iradlw=1 ndens=2,1 nhtfrq=0,1 mfilt=1,49
         offline_driver_infile='$rad_driving_data'
         empty_htapes=.true.
         fincl2='FLDS:I','FLNS:I','FLNSC:I','FLNT:I','FLNTC:I','FLUT:I',
           'FLUTC:I','QRL:I','LWCF:I','FSDS:I','FSDSC:I','FSNS:I','FSNSC:I',
           'FSNT:I','FSNTC:I','FSNTOA:I','FSNTOAC:I','FSUTOA:I','QRS:I','SWCF:I'
         /" || exit 1

    echo "control run in $rundir using $ntasks tasks"
    $runcmd $blddir/cam > $logfile 2>&1 || { echo "FAILURE-- see $logfile"; exit 1; }
    

fi

exit 0
