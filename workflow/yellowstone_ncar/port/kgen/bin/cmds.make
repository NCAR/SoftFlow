# Wrapper for useful commands

###############
# Variables
##############

SUITENAME := port

PORT := /glade/u/home/youngsun/apps/port/rrtmgp14_cam5_4_48
KGEN := /glade/u/home/youngsun/repos/github/KGen

WORKDIR := /glade/scratch/youngsun/cylcworkdir/port
MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
BINDIR := ${MAKEFILEDIR}
SUITEDIR := ${MAKEFILEDIR}/..
SOFTFLOWDIR := ${SUITEDIR}/../../../../lib/python
INCDIR := ${SUITEDIR}/inc
PYTHONDIR := ${SUITEDIR}/lib/python:${SOFTFLOWDIR}

#PRERUN_EXTRACT := "cd ${KGEN}; git checkout devel"
PRERUN_EXTRACT := "true"
#PRERUN_COVERAGE := "cd ${KGEN}; git checkout issue-81"
PRERUN_COVERAGE := "true"

#################
# Cylc useful commands
#################

register:
	cylc register ${SUITENAME} ${SUITEDIR}

validate:
	cylc validate ${SUITENAME}

graph:
	cylc graph ${SUITENAME}

stop:
	cylc stop ${SUITENAME}

ready:
	cylc reset -s ready ${SUITENAME} ${TASKID}

run:
	cylc run ${SUITENAME}

monitor:
	cylc monitor ${SUITENAME}

rmport:
	rm -f ${HOME}/.cylc/ports/${SUITENAME}

####################
# Cylc Suite Targets
####################

preprocess:
	@echo 'Begin preprocess'

copy_extract_SW_RRTMG:
	@echo 'Begin copy_extract_SW_RRTMG'
	mkdir -p ${WORKDIR}/extract_SW_RRTMG/src
	cp -R -u -p ${PORT}/* ${WORKDIR}/extract_SW_RRTMG/src

copy_extract_LW_RRTMG:
	@echo 'Begin copy_extract_LW_RRTMG'

copy_extract_SW_RRTMGP:
	@echo 'Begin copy_extract_SW_RRTMGP'

copy_extract_LW_RRTMGP:
	@echo 'Begin copy_extract_LW_RRTMGP'

copy_coverage_SW_RRTMG:
	@echo 'Begin copy_coverage_SW_RRTMG'

copy_coverage_LW_RRTMG:
	@echo 'Begin copy_coverage_LW_RRTMG'

copy_coverage_SW_RRTMGP:
	@echo 'Begin copy_coverage_SW_RRTMGP'

copy_coverage_LW_RRTMGP:
	@echo 'Begin copy_coverage_LW_RRTMGP'

extract_SW_RRTMG:
	@echo 'Begin extract_SW_RRTMG'
	${PRERUN_EXTRACT}; cd ${WORKDIR}/extract_SW_RRTMG; ${KGEN}/bin/kgen \
		--cmd-clean "true" \
		--cmd-build "cd ${WORKDIR}/extract_SW_RRTMG/src; export CYLC_CAM_ROOT=${WORKDIR}/extract_SW_RRTMG/src; export CYLC_WRKDIR=${WORKDIR}/extract_SW_RRTMG; ./f19c5aqportm-1d.sh -b" \
		--cmd-run "cd ${WORKDIR}/extract_SW_RRTMG/src; export CYLC_CAM_ROOT=${WORKDIR}/extract_SW_RRTMG/src; export CYLC_WRKDIR=${WORKDIR}/extract_SW_RRTMG; bsub -K < f19c5aqportm-1d.sh" \
		-e "/glade/u/home/youngsun/repos/github/SoftFlow/workflow/yellowstone_ncar/port/kgen/inc/exclude.ini" \
		--outdir ${WORKDIR}/extract_SW_RRTMG/kernel \
		--invocation 0:0:1,1:0:1 \
		--timing repeat=10 \
		--mpi enable \
		${WORKDIR}/extract_SW_RRTMG/src/components/cam/src/physics/rrtmg/radiation.F90:radiation:radiation_tend:rad_rrtmg_sw

extract_LW_RRTMG:
	@echo 'Begin extract_LW_RRTMG'
	#${PRERUN_EXTRACT}; ${KGEN}/bin/kgen \

extract_SW_RRTMGP:
	@echo 'Begin extract_SW_RRTMGP'
	#${PRERUN_EXTRACT}; ${KGEN}/bin/kgen \

extract_LW_RRTMGP:
	@echo 'Begin extract_LW_RRTMGP'
	#${PRERUN_EXTRACT}; ${KGEN}/bin/kgen \

coverage_SW_RRTMG:
	@echo 'Begin coverage_SW_RRTMG'
	#${PRERUN_COVERAGE}; ${KGEN}/bin/kgen \

coverage_LW_RRTMG:
	@echo 'Begin coverage_LW_RRTMG'
	#${PRERUN_COVERAGE}; ${KGEN}/bin/kgen \

coverage_SW_RRTMGP:
	@echo 'Begin coverage_SW_RRTMGP'
	#${PRERUN_COVERAGE}; ${KGEN}/bin/kgen \

coverage_LW_RRTMGP:
	@echo 'Begin coverage_LW_RRTMGP'
	#${PRERUN_COVERAGE}; ${KGEN}/bin/kgen \
