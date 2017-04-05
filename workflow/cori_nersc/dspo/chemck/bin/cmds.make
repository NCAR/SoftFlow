# Wrapper for useful commands

###############
# Variables
##############

CPU ?= KNL

TMPDIR ?= /global/cscratch1/sd/grnydawn 
WORKDIR := ${TMPDIR}/cylcworkspace/${SUITENAME}_${CPU}
MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
BINDIR := ${MAKEFILEDIR}
SUITEDIR := ${MAKEFILEDIR}/..
SOFTFLOWDIR := ${SUITEDIR}/../../../../lib/python
INCDIR := ${SUITEDIR}/inc
PYTHONDIR := ${SUITEDIR}/lib/python:${SOFTFLOWDIR}
CGROUPDIR := ${WORKDIR}/cgroup
EGROUPDIR := ${WORKDIR}/egroup
DATADIR := ${WORKDIR}/data

SUITENAME := $(shell python -c "print '_'.join('${MAKEFILEDIR}'.split('workflow')[1].split('/')[:-1])")

ALLOCTIME ?= 08:00:00

###########
# Targets
###########

cylc_register:
	cylc register ${SUITENAME} ${SUITEDIR}

cylc_unregister:
	cylc unregister ${SUITENAME}

cylc_validate:
	cylc validate ${SUITENAME}

cylc_graph:
	cylc graph ${SUITENAME}

cylc_stop:
	cylc stop ${SUITENAME}

cylc_ready:
	cylc reset -s ready ${SUITENAME} ${TASKID}

cylc_run:
	cylc run ${SUITENAME}

cylc_monitor:
	cylc monitor ${SUITENAME}

cylc_rmport:
	rm -f ${HOME}/.cylc/ports/${SUITENAME}

salloc:
	salloc -N 1 -C haswell -p regular --qos=premium -t ${ALLOCTIME}

preprocess:
    echo "" > ${TASKROOTDIR}/parse_files.txt
    
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
	mpiifort -v
	cd ${CGROUPDIR}; make -j 4 -f ./Makefile-cgroup build CPU=${CPU}

bldexp:
	mpiifort -v
	cd ${EGROUPDIR}; make -j 4 -f ./Makefile-egroup build CPU=${CPU}

runcontrol:
	cat /proc/cpuinfo | head -n 25
ifeq (${CPU},KNL)
	ulimit -s unlimited; cd ${CGROUPDIR}; srun -n 1 -c 1 --cpu_bind=cores numactl --membind=1 ./kernel.exe
else
	ulimit -s unlimited; cd ${CGROUPDIR}; srun -n 1 -c 1 ./kernel.exe
endif

runexp:
	cat /proc/cpuinfo | head -n 25
ifeq (${CPU},KNL)
	ulimit -s unlimited; cd ${EGROUPDIR}; srun -n 1 -c 1 --cpu_bind=cores numactl --membind=1 ./kernel.exe
else
	ulimit -s unlimited; cd ${EGROUPDIR}; srun -n 1 -c 1 ./kernel.exe
endif

checkdiff:
	export PYTHONPATH=${PYTHONDIR}:${PYTHONPATH}; statdiff.py ${BASELINE} ${FOLLOWUP}

genoutput:
	export PYTHONPATH=${PYTHONDIR}:${PYTHONPATH}; genoutput.py

