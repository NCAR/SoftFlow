# Wrapper for useful commands

###############
# Variables
##############

#KERNELREPO := https://github.com/NCAR/kernelOptimization
#CHEMV4 := all/WACCM_imp_sol_vector/v04
#CHEMDATA := all/WACCM_imp_sol_vector/data

WORKDIR := /lustre/scratch/youngsun/cylcworkspace/${SUITENAME}
MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
BINDIR := ${MAKEFILEDIR}
SUITEDIR := ${MAKEFILEDIR}/..
INCDIR := ${SUITEDIR}/inc
CGROUPDIR := ${WORKDIR}/cgroup
EGROUPDIR := ${WORKDIR}/egroup
DATADIR := ${WORKDIR}/data

SUITENAME := $(shell python -c "print '_'.join('${MAKEFILEDIR}'.split('workflow')[1].split('/')[:-1])")

###########
# Targets
###########

cylc_register:
	cylc register ${SUITENAME} ${SUITEDIR}

cylc_unregister:
	cylc unregister ${SUITENAME}

cylc_validate:
	cylc validate ${SUITENAME}

cylc_stop:
	cylc stop ${SUITENAME}

copyfiles:
	mkdir -p ${WORKDIR}/cgroup
	mkdir -p ${WORKDIR}/egroup
	mkdir -p ${WORKDIR}/data
	yes | cp -fp ${SUITEDIR}/src/* ${WORKDIR}/cgroup
	yes | cp -fp ${SUITEDIR}/src/* ${WORKDIR}/egroup
	yes | cp -fp ${SUITEDIR}/data/* ${WORKDIR}/data
	yes | cp -fp ${INCDIR}/Makefile-cgroup ${WORKDIR}/cgroup
	yes | cp -fp ${INCDIR}/Makefile-egroup ${WORKDIR}/egroup
	#mv -f ${WORKDIR}/egroup/mo_nln_matrix.F90 ${WORKDIR}/egroup/mo_nln_matrix.F90.bak
	#yes | cp -fp ${INCDIR}/mo_nln_matrix.F90-egroup ${WORKDIR}/egroup/mo_nln_matrix.F90

bldcontrol:
	source ${HOME}/intel.compiler; cd ${CGROUPDIR}; make -j 6 -f ./Makefile-cgroup build CPU=KNL

bldexp:
	source ${HOME}/intel.compiler; cd ${EGROUPDIR}; make -j 6 -f ./Makefile-egroup build CPU=KNL

runcontrol:
	source ${HOME}/intel.compiler; ulimit -s unlimited; cd ${CGROUPDIR}; srun -n 1 numactl --membind=1 ./kernel.exe

runexp:
	source ${HOME}/intel.compiler; ulimit -s unlimited; cd ${EGROUPDIR}; srun -n 1 numactl --membind=1 ./kernel.exe
