# Wrapper for useful commands

###############
# Variables
##############

PORT := /glade/u/home/youngsun/apps/port/rrtmgp14_cam5_4_48
KGEN := /glade/u/home/youngsun/repos/github/KGen

MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SUITENAME := $(shell python -c "print '_'.join('${MAKEFILEDIR}'.split('workflow')[1].split('/')[:-1])")
WORKDIR := /glade/scratch/youngsun/cylcworkdir/port

SUITEDIR := ${MAKEFILEDIR}/..
INCDIR := ${SUITEDIR}/inc

#PRERUN_EXTRACT := "cd ${KGEN}; git checkout devel"
PRERUN_EXTRACT := "true"
#PRERUN_COVERAGE := "cd ${KGEN}; git checkout issue-81"
PRERUN_COVERAGE := "true"

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

####################
# Cylc Suite Targets
####################

copy:
	@echo 'Copying ${ACTION}_${WAVE}_${TEST}'
	mkdir -p ${WORKDIR}/${ACTION}_${WAVE}_${TEST}/src
	cp -R -u -p ${PORT}/* ${WORKDIR}/${ACTION}_${WAVE}_${TEST}/src
ifeq (${ACTION},extract)
ifeq (${TEST},RRTMGP)
	cp -f ${INCDIR}/radiation.F90 ${WORKDIR}/${ACTION}_${WAVE}_${TEST}/src/components/cam/src/physics/rrtmgp
	cp -f ${INCDIR}/mo_rrtmgp_sw.F90 ${WORKDIR}/${ACTION}_${WAVE}_${TEST}/src/components/cam/src/physics/rrtmgp/ext
	cp -f ${INCDIR}/mo_rrtmgp_lw.F90 ${WORKDIR}/${ACTION}_${WAVE}_${TEST}/src/components/cam/src/physics/rrtmgp/ext
	cp -f ${INCDIR}/mo_gas_concentrations.F90 ${WORKDIR}/${ACTION}_${WAVE}_${TEST}/src/components/cam/src/physics/rrtmgp/ext
endif
endif

run:
	@echo 'Running ${ACTION}_${WAVE}_${TEST}'
	${PRERUN_EXTRACT}; cd ${WORKDIR}/${ACTION}_${WAVE}_${TEST}; ${KGEN}/bin/kgen \
		--cmd-clean "rm -rf ${WORKDIR}/${ACTION}_${WAVE}_${TEST}/${SCRIPT}_intel_bld/*" \
		--cmd-build "cd ${WORKDIR}/${ACTION}_${WAVE}_${TEST}/src; export CYLC_CAM_ROOT=${WORKDIR}/${ACTION}_${WAVE}_${TEST}/src; export CYLC_WRKDIR=${WORKDIR}/${ACTION}_${WAVE}_${TEST}; ./${SCRIPT}-1d.sh -b" \
		--cmd-run "cd ${WORKDIR}/${ACTION}_${WAVE}_${TEST}/src; export CYLC_CAM_ROOT=${WORKDIR}/${ACTION}_${WAVE}_${TEST}/src; export CYLC_WRKDIR=${WORKDIR}/${ACTION}_${WAVE}_${TEST}; bsub -K < ${SCRIPT}-1d.sh" \
		-e "/glade/u/home/youngsun/repos/github/SoftFlow/workflow/yellowstone_ncar/port/kgen/inc/exclude.ini" \
		--outdir ${WORKDIR}/${ACTION}_${WAVE}_${TEST}/output \
		--invocation ${INVOKE} \
		--timing repeat=10 \
		--mpi enable \
		${WORKDIR}/${ACTION}_${WAVE}_${TEST}/${CALLSITE}
