# Wrapper for useful commands

###############
# Variables
##############

CPU ?= SNB

# fdv
#RRTMG_EXPERIMENT := /lustre/scratch/youngsun/cylcworkspace/exfold_SNB/optimize/fdv/rrtmgp_lw.v2
#WORKDIR := /lustre/scratch/youngsun/cylcworkspace/exfold_SNB/optimize/fdv/folding

# exp
#RRTMG_EXPERIMENT := /lustre/scratch/youngsun/cylcworkspace/exfold_SNB/optimize/exp/rrtmgp_lw.v2
#WORKDIR := /lustre/scratch/youngsun/cylcworkspace/exfold_SNB/optimize/exp/folding

# inline
#RRTMG_EXPERIMENT := /lustre/scratch/youngsun/cylcworkspace/exfold_SNB/optimize/inline/rrtmgp_lw.v2
#WORKDIR := /lustre/scratch/youngsun/cylcworkspace/exfold_SNB/optimize/inline/folding

# l1dcm
#RRTMG_EXPERIMENT := /lustre/scratch/youngsun/cylcworkspace/exfold_SNB/optimize/l1dcm/rrtmgp_lw.v2
#WORKDIR := /lustre/scratch/youngsun/cylcworkspace/exfold_SNB/optimize/l1dcm/folding

# elemental
RRTMG_EXPERIMENT := /lustre/scratch/youngsun/cylcworkspace/exfold_SNB/optimize/elemental/rrtmgp_lw.v2
WORKDIR := /lustre/scratch/youngsun/cylcworkspace/exfold_SNB/optimize/elemental/folding


MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
BINDIR := ${MAKEFILEDIR}
SUITEDIR := ${MAKEFILEDIR}/..
SOFTFLOWDIR := ${SUITEDIR}/../../../..
BASHDIR := ${SUITEDIR}/../../../../lib/bash
INCDIR := ${SUITEDIR}/inc
PYTHONPATH := ${SUITEDIR}/lib/python:${SOFTFLOWDIR}/lib/python:${PYTHONPATH}
EGROUPDIR := ${WORKDIR}

SUITENAME := $(shell python -c "print '_'.join('${MAKEFILEDIR}'.split('workflow')[1].split('/')[:-1])")

ORG_FOLDING := /lustre/scratch/youngsun/cylcworkspace/exfold_SNB/egroup/folding/0302_2017:original
OPT_FOLDING := ${WORKDIR}/kernel/experiment:optimized

EXTRAE_HOME ?= /ncar/asap/opt/extrae/3.3.0/snb/intel/17.0.0
FOLDING_HOME ?= /ncar/asap/opt/folding/1.0.2
PLOT_SCRIPT ?= ${SOFTFLOWDIR}/lib/python/plot_exfold.py

#################
# Cylc useful commands
#################

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

#################
# Other useful commands
#################


####################
# Cylc Suite Targets
####################

preprocess:
	@echo 'Begin preprocess'

copy_experiment:
	@echo 'Begin copy_experiment'
	mkdir -p ${EGROUPDIR}/kernel
	cp -R -p ${RRTMG_EXPERIMENT}/* ${EGROUPDIR}
	#cp -f ${INCDIR}/mo_rrtmgp_lw.F90 ${EGROUPDIR}/kernel
	cp -f ${INCDIR}/extrae.xml ${EGROUPDIR}/kernel
	cp -f ${INCDIR}/Makefile.experiment ${EGROUPDIR}/kernel/Makefile

clean_experiment:
	@echo 'Begin clean_experiment'
	cd ${EGROUPDIR}/kernel; make clean

build_experiment:
	@echo 'Begin build_experiment'
	cd ${EGROUPDIR}/kernel; make -j 4 build
	#cp -f ${INCDIR}/mo_rrtmgp_lw.F90.orig ${EGROUPDIR}/kernel/mo_rrtmgp_lw.F90
	#cp -f ${INCDIR}/Makefile.experiment.orig ${EGROUPDIR}/kernel/Makefile
	#

run_experiment:
	@echo 'Begin run_experiment'
	cd ${EGROUPDIR}/kernel; \
		sed "s,EXECUTABLE,${EGROUPDIR}/kernel/kernel.exe,g" ${BINDIR}/job.${CPU}.submit > ./job.${CPU}.submit; \
		${BASHDIR}/sbatchwait ./job.${CPU}.submit

collect_experiment:
	@echo 'Begin collect_experiment'
	cd ${EGROUPDIR}/kernel; \
	${EXTRAE_HOME}/bin/mpi2prv -f TRACE.mpits -o experiment.prv

fold_experiment:
	@echo 'Begin fold_experiment'
	cd ${EGROUPDIR}/kernel; \
		${FOLDING_HOME}/bin/folding ./experiment.prv "User function"

plot:
	@echo 'Begin plot'
	cd ${EGROUPDIR}; python ${PLOT_SCRIPT} -t ${ORG_FOLDING} ${OPT_FOLDING}
