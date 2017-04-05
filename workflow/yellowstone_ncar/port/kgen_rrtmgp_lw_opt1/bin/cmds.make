# Wrapper for useful commands

###############
# Variables
##############

PORT := /glade/u/home/youngsun/apps/port/rrtmgp14_cam5_4_48
CASE := opt1_LW_RRTMGP
SCRIPT := f19c5aqrpportm
KGEN := /glade/u/home/youngsun/repos/github/KGen

WORKDIR := /glade/scratch/youngsun/cylcworkdir/port
MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SUITEDIR := ${MAKEFILEDIR}/..
INCDIR := ${SUITEDIR}/inc
CALLSITE := ${WORKDIR}/${CASE}/src/components/cam/src/physics/rrtmgp/radiation.F90:radiation:radiation_tend:rrtmgp_lw

SUITENAME := $(shell python -c "print '_'.join('${MAKEFILEDIR}'.split('workflow')[1].split('/')[:-1])")

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
	@echo 'Copying'
	mkdir -p ${WORKDIR}/${CASE}/src
	cp -R -u -p ${PORT}/* ${WORKDIR}/${CASE}/src
	cp -f ${INCDIR}/radiation.F90 ${WORKDIR}/${CASE}/src/components/cam/src/physics/rrtmgp
	cp -f ${INCDIR}/mo_gas_optics_kernels.F90 ${WORKDIR}/${CASE}/src/components/cam/src/physics/rrtmgp/ext
	cp -f ${INCDIR}/mo_optical_props_kernels.F90 ${WORKDIR}/${CASE}/src/components/cam/src/physics/rrtmgp/ext
	cp -f ${INCDIR}/mo_rrtmgp_lw.F90 ${WORKDIR}/${CASE}/src/components/cam/src/physics/rrtmgp/ext
	cp -f ${INCDIR}/mo_rrtmgp_lw_solver.F90 ${WORKDIR}/${CASE}/src/components/cam/src/physics/rrtmgp/ext
	cp -f ${INCDIR}/mo_rrtmgp_sw.F90 ${WORKDIR}/${CASE}/src/components/cam/src/physics/rrtmgp/ext
	cp -f ${INCDIR}/mo_rrtmgp_sw_solver.F90 ${WORKDIR}/${CASE}/src/components/cam/src/physics/rrtmgp/ext
	cp -f ${INCDIR}/mo_rrtmgp_solver_kernels.F90 ${WORKDIR}/${CASE}/src/components/cam/src/physics/rrtmgp/ext

run:
	@echo 'Running'
	cd ${WORKDIR}/${CASE}; ${KGEN}/bin/kgen \
		--cmd-clean "rm -rf ${WORKDIR}/${CASE}/${SCRIPT}_intel_bld/*" \
		--cmd-build "cd ${WORKDIR}/${CASE}/src; export CYLC_CAM_ROOT=${WORKDIR}/${CASE}/src; export CYLC_WRKDIR=${WORKDIR}/${CASE}; ./${SCRIPT}-1d.sh -b" \
		--cmd-run "cd ${WORKDIR}/${CASE}/src; export CYLC_CAM_ROOT=${WORKDIR}/${CASE}/src; export CYLC_WRKDIR=${WORKDIR}/${CASE}; bsub -K < ${SCRIPT}-1d.sh" \
		-e "/glade/u/home/youngsun/repos/github/SoftFlow/workflow/yellowstone_ncar/port/kgen/inc/exclude.ini" \
		--outdir ${WORKDIR}/${CASE}/output \
		--mpi enable \
		${CALLSITE}
