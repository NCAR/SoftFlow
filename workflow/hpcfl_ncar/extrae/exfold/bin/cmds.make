# Wrapper for useful commands

###############
# Variables
##############

SUITENAME := exfold
CPU ?= SNB

HOMME_CONTROL := /users/youngsun/kernels/port/rrtmg_lw
HOMME_EXPERIMENT := /users/youngsun/kernels/port/rrtmgp_lw.v2

WORKDIR := /lustre/scratch/youngsun/cylcworkspace/${SUITENAME}_${CPU}
MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
BINDIR := ${MAKEFILEDIR}
SUITEDIR := ${MAKEFILEDIR}/..
SOFTFLOWDIR := ${SUITEDIR}/../../../../lib/python
BASHDIR := ${SUITEDIR}/../../../../lib/bash
INCDIR := ${SUITEDIR}/inc
PYTHONPATH := ${SUITEDIR}/lib/python:${SOFTFLOWDIR}${PYTHONPATH}
CGROUPDIR := ${WORKDIR}/cgroup
EGROUPDIR := ${WORKDIR}/egroup

EXTRAE_HOME ?= /ncar/asap/opt/extrae/3.3.0/snb/intel/17.0.0
FOLDING_HOME ?= /ncar/asap/opt/folding/1.0.2

#################
# Cylc useful commands
#################

cylc_register:
	cylc register ${SUITENAME} ${SUITEDIR}

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

#################
# Other useful commands
#################


####################
# Cylc Suite Targets
####################

preprocess:
	@echo 'Begin preprocess'

copy_control:
	@echo 'Begin copy_control'
	mkdir -p ${CGROUPDIR}
	cp -R -u -p ${HOMME_CONTROL}/* ${CGROUPDIR}
	cp -f ${INCDIR}/extrae.xml ${CGROUPDIR}/kernel
	cp -f ${INCDIR}/rrtmg_lw_rad.f90 ${CGROUPDIR}/kernel
	cp -f ${INCDIR}/Makefile.control ${CGROUPDIR}/kernel/Makefile

copy_experiment:
	@echo 'Begin copy_experiment'
	mkdir -p ${EGROUPDIR}
	cp -R -u -p ${HOMME_EXPERIMENT}/* ${EGROUPDIR}
	cp -f ${INCDIR}/extrae.xml ${EGROUPDIR}/kernel
	cp -f ${INCDIR}/mo_rrtmgp_lw.F90 ${EGROUPDIR}/kernel
	cp -f ${INCDIR}/Makefile.experiment ${EGROUPDIR}/kernel/Makefile

clean_control:
	@echo 'Begin clean_control'
	cd ${CGROUPDIR}/kernel; make clean

clean_experiment:
	@echo 'Begin clean_experiment'
	cd ${EGROUPDIR}/kernel; make clean

build_control:
	@echo 'Begin build_control'
	cd ${CGROUPDIR}/kernel; make -j 4 build
	#cp -f ${INCDIR}/rrtmg_lw_rad.f90.orig ${CGROUPDIR}/kernel/rrtmg_lw_rad.f90
	#cp -f ${INCDIR}/Makefile.control.orig ${CGROUPDIR}/kernel/Makefile

build_experiment:
	@echo 'Begin build_experiment'
	cd ${EGROUPDIR}/kernel; make -j 4 build
	#cp -f ${INCDIR}/mo_rrtmgp_lw.F90.orig ${EGROUPDIR}/kernel/mo_rrtmgp_lw.F90
	#cp -f ${INCDIR}/Makefile.experiment.orig ${EGROUPDIR}/kernel/Makefile
	#
run_control:
	@echo 'Begin run_control'
	cd ${CGROUPDIR}/kernel; \
		sed "s,EXECUTABLE,${CGROUPDIR}/kernel/kernel.exe,g" ${BINDIR}/job.${CPU}.submit > ./job.${CPU}.submit; \
		${BASHDIR}/sbatchwait ./job.${CPU}.submit

run_experiment:
	@echo 'Begin run_experiment'
	cd ${EGROUPDIR}/kernel; \
		sed "s,EXECUTABLE,${EGROUPDIR}/kernel/kernel.exe,g" ${BINDIR}/job.${CPU}.submit > ./job.${CPU}.submit; \
		${BASHDIR}/sbatchwait ./job.${CPU}.submit

collect_control:
	@echo 'Begin collect_control'
	cd ${CGROUPDIR}/kernel; \
	${EXTRAE_HOME}/bin/mpi2prv -f TRACE.mpits -o control.prv

collect_experiment:
	@echo 'Begin collect_experiment'
	cd ${EGROUPDIR}/kernel; \
	${EXTRAE_HOME}/bin/mpi2prv -f TRACE.mpits -o experiment.prv

fold_control:
	@echo 'Begin fold_control'
	cd ${CGROUPDIR}/kernel; \
		${FOLDING_HOME}/bin/folding control.prv "User function"

fold_experiment:
	@echo 'Begin fold_experiment'
	cd ${EGROUPDIR}/kernel; \
		${FOLDING_HOME}/bin/folding experiment.prv "User function"

plot:
	@echo 'Not implemented yet.'
