# Wrapper for useful commands

###############
# Variables
##############

TEST ?= perfTest
GROUP ?= control
CPU ?= SNB

RAW_TRACE := /users/youngsun/trepo/temp/${TEST}_${GROUP}_yellowstone_ncar_extrae_homme.tar


WORKDIR := /lustre/scratch/youngsun/cylcworkspace/exfold_homme_${CPU}/${TEST}
MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
BINDIR := ${MAKEFILEDIR}
SUITEDIR := ${MAKEFILEDIR}/..
SOFTFLOWDIR := ${SUITEDIR}/../../../..
BASHDIR := ${SUITEDIR}/../../../../lib/bash
INCDIR := ${SUITEDIR}/inc
PYTHONPATH := ${SUITEDIR}/lib/python:${SOFTFLOWDIR}/lib/python:${PYTHONPATH}

SUITENAME := $(shell python -c "print '_'.join('${MAKEFILEDIR}'.split('workflow')[1].split('/')[:-1])")

CFOLDING := ${WORKDIR}/control/${TEST}:original
EFOLDING := ${WORKDIR}/experiment/${TEST}:optimized

EXTRAE_HOME ?= /ncar/asap/opt/extrae/3.3.0/snb/intel/17.0.0
FOLDING_HOME ?= /ncar/asap/opt/folding/1.0.2
#PLOT_SCRIPT ?= ${SOFTFLOWDIR}/lib/python/plot_exfold.py
PLOT_SCRIPT ?= ${SOFTFLOWDIR}/lib/python/plot_fill_exfold.py

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

copy:
	@echo 'Begin copy'
	mkdir -p ${WORKDIR}/${GROUP}
	tar -xvf ${RAW_TRACE} -C ${WORKDIR}/${GROUP}

fold:
	@echo 'Begin foldding'
	cd ${WORKDIR}/${GROUP}; ${FOLDING_HOME}/bin/folding ./${TEST}.prv "User function"

plot:
	@echo 'Begin plot'
	#cd ${WORKDIR}; python ${PLOT_SCRIPT} -t ${CFOLDING} ${EFOLDING}
	cd ${WORKDIR}; python ${PLOT_SCRIPT} -t -e PAPI_L1_DCM -f compute_and_apply_rhs,euler_step,advance_hypervis_dp ${CFOLDING} ${EFOLDING}
	#python /users/youngsun/repos/github/SoftFlow/lib/python/plot_exfold.py -t -e PAPI_FDV_INS_per_ins,PAPI_TLB_DM_per_ins,PAPI_SR_INS_per_ins,PAPI_L3_TCM_per_ins,SIMD_FP_256:PACKED_DOUBLE_per_ins cgroup/control:ver3 egroup/experiment:ver4
