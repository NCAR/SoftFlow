# Wrapper for useful commands

###############
# Variables
##############

CPU ?= SNB

CONTROL_EXTRAE_TRACE := /users/youngsun/trepo/temp/control_yellowstone_ncar_port_extrae_rrtmgp_lw_opt7.tar
MIDDLESTAGE_EXTRAE_TRACE := /users/youngsun/trepo/temp/middlestage_yellowstone_ncar_port_extrae_rrtmgp_lw_opt7.tar
EXPERIMENT_EXTRAE_TRACE := /users/youngsun/trepo/temp/experiment_yellowstone_ncar_port_extrae_rrtmgp_lw_opt7.tar

WORKDIR := /lustre/scratch/youngsun/cylcworkspace/exfold_opt7_${CPU}
MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SUITENAME := $(shell python -c "print '_'.join('${MAKEFILEDIR}'.split('workflow')[1].split('/')[:-1])")

BINDIR := ${MAKEFILEDIR}
SUITEDIR := ${MAKEFILEDIR}/..
SOFTFLOWDIR := ${SUITEDIR}/../../../..
BASHDIR := ${SUITEDIR}/../../../../lib/bash
INCDIR := ${SUITEDIR}/inc
PYTHONPATH := ${SUITEDIR}/lib/python:${SOFTFLOWDIR}/lib/python:${PYTHONPATH}
CGROUPDIR := ${WORKDIR}/cgroup
MGROUPDIR := ${WORKDIR}/mgroup
EGROUPDIR := ${WORKDIR}/egroup

CFOLDING := ${WORKDIR}/cgroup/control:kernel_ver3
MFOLDING := ${WORKDIR}/mgroup/middlestage:kernel_ver6
EFOLDING := ${WORKDIR}/egroup/experiment:kernel_ver7

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

copy_control:
	@echo 'Begin copy_control'
	mkdir -p ${CGROUPDIR}
	tar -xvf ${CONTROL_EXTRAE_TRACE} -C ${CGROUPDIR}

copy_middlestage:
	@echo 'Begin copy_middlestage'
	mkdir -p ${MGROUPDIR}
	tar -xvf ${EXPERIMENT_EXTRAE_TRACE} -C ${EGROUPDIR}

copy_experiment:
	@echo 'Begin copy_experiment'
	mkdir -p ${EGROUPDIR}
	tar -xvf ${MIDDLESTAGE_EXTRAE_TRACE} -C ${MGROUPDIR}

fold_control:
	@echo 'Begin fold_control'
	cd ${CGROUPDIR}; ${FOLDING_HOME}/bin/folding ./control.prv "User function"

fold_middlestage:
	@echo 'Begin fold_middlestage'
	cd ${MGROUPDIR}; ${FOLDING_HOME}/bin/folding ./middlestage.prv "User function"

fold_experiment:
	@echo 'Begin fold_experiment'
	cd ${EGROUPDIR}; ${FOLDING_HOME}/bin/folding ./experiment.prv "User function"

plot:
	@echo 'Begin plot'
	cd ${WORKDIR}; python ${PLOT_SCRIPT} -t ${CFOLDING} ${MFOLDING} ${EFOLDING}
	#python /users/youngsun/repos/github/SoftFlow/lib/python/plot_exfold.py -t -e PAPI_FDV_INS_per_ins,PAPI_TLB_DM_per_ins,PAPI_SR_INS_per_ins,PAPI_L3_TCM_per_ins,SIMD_FP_256:PACKED_DOUBLE_per_ins cgroup/control:ver3 egroup/experiment:ver4
