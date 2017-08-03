# Wrapper for useful commands

###############
# Variables
##############

CESM := /glade/u/home/youngsun/apps/cesm/cesm1_5_beta07
KGEN := /glade/u/home/youngsun/repos/github/KGen

MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SUITENAME := $(shell python -c "print '_'.join('${MAKEFILEDIR}'.split('workflow')[1].split('/')[:-1])")
WORKDIR := /glade/scratch/youngsun/cylcworkspace/${SUITENAME}

SUITEDIR := ${MAKEFILEDIR}/..
INCDIR := ${SUITEDIR}/inc


CALLSITE :=  components/cam/src/physics/cam/micro_mg_cam.F90:micro_mg_cam:micro_mg_cam_tend_pack:micro_mg_tend2_0

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
	@echo 'Copying CESM'
	mkdir -p ${WORKDIR}/src
	cp -R -p -f ${CESM}/* ${WORKDIR}/src

createcase:
	@echo 'Creating a CESM case'
	rm -rf ${WORKDIR}/case
	cd ${WORKDIR}/src/cime/scripts; ./cesm_setup -clean; ./create_newcase \
		-mach yellowstone \
		-res ne16_ne16 \
		-compset FC5 \
		-case ${WORKDIR}/case \
		-project STDD0002

configcase:
	@echo 'Configuring a CESM case'
	cd ${WORKDIR}/case; \
	./xmlchange -f env_build.xml -id CAM_CONFIG_OPTS -val "-microphys mg2 -clubb_sgs" -a; \
	./xmlchange -f env_build.xml -id BATCHSUBMIT -val "bsub -K"; \
	./case.setup

	#./xmlchange BATCHSUBMIT="bsub -K";
	#
run:
	@echo 'Running KGEN' 
	mkdir -p ${WORKDIR}/output
	cd ${WORKDIR}/output; ${KGEN}/bin/kgen \
		--cmd-clean "cd ${WORKDIR}/case; ./case.clean_build" \
		--cmd-build "cd ${WORKDIR}/case; ./case.build" \
		--cmd-run "cd ${WORKDIR}/case; ./case.submit" \
		--outdir ${WORKDIR}/output \
		--intrinsic skip,except=shr_spfn_mod:shr_spfn_gamma_nonintrinsic_r8:sum \
		--skip elapsedtime \
		--mpi comm=mpicom,use="spmd_utils:mpicom" \
		--state-switch type=copy,directory=${WORKDIR}/case/SourceMods/src.cam,clean="rm -f ${WORKDIR}/case/SourceMods/src.cam/*" \
		--source alias=/glade2/scratch2:/glade/scratch \
		--repr-etime minval=1.0E-7,maxval=2.0E-5 \
		--timing repeat=10 \
		--mpi enable \
		--openmp enable \
		${WORKDIR}/src/${CALLSITE}


		#--skip coverage \
		#-e "${INCDIR}/exclude.ini" \
