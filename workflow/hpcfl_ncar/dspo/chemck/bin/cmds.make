# Wrapper for useful commands

###############
# Variables
##############

SUITENAME := chemck
CPU ?= KNL

WORKDIR := /lustre/scratch/youngsun/cylcworkspace/${SUITENAME}_${CPU}
MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
BINDIR := ${MAKEFILEDIR}
SUITEDIR := ${MAKEFILEDIR}/..
INCDIR := ${SUITEDIR}/inc
PYTHONDIR := ${SUITEDIR}/lib/python
CGROUPDIR := ${WORKDIR}/cgroup
EGROUPDIR := ${WORKDIR}/egroup
DATADIR := ${WORKDIR}/data

###########
# Targets
###########

register:
	cylc register ${SUITENAME} ${SUITEDIR}

validate:
	cylc validate ${SUITENAME}

stop:
	cylc stop ${SUITENAME}

copyfiles:
	mkdir -p ${WORKDIR}/cgroup
	mkdir -p ${WORKDIR}/egroup
	mkdir -p ${WORKDIR}/data
	yes | cp -fp ${SUITEDIR}/src/* ${WORKDIR}/cgroup
	yes | cp -fp ${SUITEDIR}/src/* ${WORKDIR}/egroup
	yes | cp -fp ${SUITEDIR}/../chemv4/data/* ${WORKDIR}/data
	yes | cp -fp ${INCDIR}/Makefile-cgroup ${WORKDIR}/cgroup
	yes | cp -fp ${INCDIR}/Makefile-egroup ${WORKDIR}/egroup
	#mv -f ${WORKDIR}/egroup/mo_nln_matrix.F90 ${WORKDIR}/egroup/mo_nln_matrix.F90.bak
	#yes | cp -fp ${INCDIR}/mo_nln_matrix.F90-egroup ${WORKDIR}/egroup/mo_nln_matrix.F90

bldcontrol:
	source ${HOME}/intel.compiler; cd ${CGROUPDIR}; make -j 4 -f ./Makefile-cgroup build CPU=${CPU}

bldexp:
	source ${HOME}/intel.compiler; cd ${EGROUPDIR}; make -j 4 -f ./Makefile-egroup build CPU=${CPU}

runcontrol:
ifeq (${CPU},KNL)
	source ${HOME}/intel.compiler; ulimit -s unlimited; cd ${CGROUPDIR}; srun -n 1 numactl --membind=1 ./kernel.exe
else
	source ${HOME}/intel.compiler; ulimit -s unlimited; cd ${CGROUPDIR}; srun -n 1 ./kernel.exe
endif

runexp:
ifeq (${CPU},KNL)
	source ${HOME}/intel.compiler; ulimit -s unlimited; cd ${EGROUPDIR}; srun -n 1 numactl --membind=1 ./kernel.exe
else
	source ${HOME}/intel.compiler; ulimit -s unlimited; cd ${EGROUPDIR}; srun -n 1 ./kernel.exe
endif

checkdiff:
	export PYTHONPATH=${PYTHONDIR}:${PYTHONPATH}; statdiff.py ${BASELINE} ${FOLLOWUP}
