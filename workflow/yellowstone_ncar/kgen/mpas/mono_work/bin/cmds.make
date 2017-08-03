# Wrapper for useful commands

###############
# Variables
##############

MPAS := /glade/scratch/youngsun/kgenmpas/init
KGEN := /glade/u/home/youngsun/repos/github/KGen

MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SUITENAME := $(shell python -c "print '_'.join('${MAKEFILEDIR}'.split('workflow')[1].split('/')[:-1])")
WORKDIR := /glade/scratch/youngsun/cylcworkspace/${SUITENAME}

SUITEDIR := ${MAKEFILEDIR}/..
INCDIR := ${SUITEDIR}/inc

TARGETFILE := core_atmosphere/src/core_atmosphere/dynamics/mpas_atm_time_integration.F
CALLSITE :=  atm_time_integration:atm_advance_scalars_mono:atm_advance_scalars_mono_work

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
	@echo 'Copying MPAS'
	mkdir -p ${WORKDIR}/src
	cp -R -p -f ${MPAS}/* ${WORKDIR}/src

run:
	@echo 'Running KGEN' 
	mkdir -p ${WORKDIR}/output
	cd ${WORKDIR}/output; ${KGEN}/bin/kgen \
		--cmd-clean "cd ${WORKDIR}/src/; ./clean_core.sh" \
		--cmd-build "cd ${WORKDIR}/src; ./buildMPASPgi.sh" \
		--cmd-run "cd ${WORKDIR}/src/benchmark; bsub -K < job_core.sh" \
		--outdir ${WORKDIR}/output \
		--skip coverage \
		--source alias=/glade2/scratch2:/glade/scratch \
		--timing repeat=1 \
		--mpi enable \
		--openmp enable \
		-e ${INCDIR}/exclude.ini \
		${WORKDIR}/src/${TARGETFILE}:${CALLSITE}


		#--repr-etime minval=1.0E-7,maxval=2.0E-5 \
		#--state-switch type=copy,directory=${WORKDIR}/case/SourceMods/src.cam,clean="rm -f ${WORKDIR}/case/SourceMods/src.cam/*" \
		#--mpi comm=mpicom,use="spmd_utils:mpicom" \
		#--skip elapsedtime \
		#--intrinsic skip,except=shr_spfn_mod:shr_spfn_gamma_nonintrinsic_r8:sum \
		#-e "${INCDIR}/exclude.ini" \
