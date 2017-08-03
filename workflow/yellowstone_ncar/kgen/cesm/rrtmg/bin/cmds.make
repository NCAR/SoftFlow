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

CALLSITE :=  components/cam/src/physics/rrtmg/radlw.F90:radlw:rad_rrtmg_lw:rrtmg_lw

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
	cd ${WORKDIR}/src/cime/scripts; ./create_newcase \
		-mach yellowstone \
		-res ne16_ne16 \
		-compset FC5 \
		-case ${WORKDIR}/case \
		-project STDD0002

configcase:
	@echo 'Configuring a CESM case'
	cd ${WORKDIR}/case; \
	./case.setup -clean; \
	./xmlchange -f env_build.xml -id CAM_CONFIG_OPTS -val "-microphys mg2 -clubb_sgs" -a; \
	./xmlchange -f env_build.xml -id BATCHSUBMIT -val "bsub -K"; \
	./case.setup

# for elapsedtime
#	./xmlchange NTASKS_ATM=1; \
#	./xmlchange NTHRDS_ATM=2; \
#	./xmlchange ROOTPE_ATM=0; \

run:
	@echo 'Running KGEN' 
	mkdir -p ${WORKDIR}/output
	cd ${WORKDIR}/output; ${KGEN}/bin/kgen \
		--cmd-clean "cd ${WORKDIR}/case; ./case.clean_build" \
		--cmd-build "cd ${WORKDIR}/case; ./case.build" \
		--cmd-run "cd ${WORKDIR}/case; ./case.submit" \
		--outdir ${WORKDIR}/output \
		--intrinsic skip,except=shr_spfn_mod:shr_spfn_gamma_nonintrinsic_r8:sum \
		--mpi comm=mpicom,use="spmd_utils:mpicom" \
		--skip coverage \
		--state-switch type=copy,directory=${WORKDIR}/case/SourceMods/src.cam,clean="rm -f ${WORKDIR}/case/SourceMods/src.cam/*" \
		--source alias=/glade2/scratch2:/glade/scratch \
        --add-mpi-frame np=30,mpiexec=mpirun \
		--timing repeat=1 \
		--repr-etime minval=3.0E-4,maxval=8.0E-3,timer=cputime \
		--mpi enable \
		--openmp enable \
		${WORKDIR}/src/${CALLSITE}

		#--skip elapsedtime \
		#-e "${INCDIR}/exclude.ini" \
