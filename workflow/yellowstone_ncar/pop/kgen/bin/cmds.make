# Wrapper for useful commands

###############
# Variables
##############

POP := /glade/u/home/youngsun/apps/cesm/cesm2_0_alpha06b_marbl_dev_n31_cesm_pop_2_1_20170216
KGEN := /glade/u/home/youngsun/repos/github/KGen

WORKDIR := /glade/scratch/youngsun/cylcworkspace/pop
MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SUITEDIR := ${MAKEFILEDIR}/..
INCDIR := ${SUITEDIR}/inc

SUITENAME := $(shell python -c "print '_'.join('${MAKEFILEDIR}'.split('workflow')[1].split('/')[:-1])")

CALLSITE :=  components/pop/source/passive_tracers.F90:passive_tracers:set_interior_passive_tracers_3D:ecosys_driver_set_interior

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
	@echo 'Copying ${ACTION}'
	mkdir -p ${WORKDIR}/${ACTION}/src
	cp -R -u -p ${POP}/* ${WORKDIR}/${ACTION}/src
	#cp ${INCDIR}/createcase ${WORKDIR}/${ACTION}

createcase:
	@echo 'Creating ${ACTION} case'
	rm -rf ${WORKDIR}/${ACTION}/case
	cd ${WORKDIR}/${ACTION}/src/cime/scripts; ./create_newcase \
		-mach yellowstone \
		-res T62_g16 \
		-compset GECO \
		-case ${WORKDIR}/${ACTION}/case \
		-project STDD0002

configcase:
	@echo 'Configuring ${ACTION} case'
	cd ${WORKDIR}/${ACTION}/case; \
	./xmlchange MAX_TASKS_PER_NODE=16,PES_PER_NODE=16; \
	./xmlchange NTASKS_ATM=16,NTASKS_WAV=16,NTASKS_GLC=16,NTASKS_ROF=16,NTASKS_LND=16,NTASKS_ESP=16,NTHRDS_ESP=2; \
	./xmlchange ROOTPE_CPL=16,ROOTPE_ICE=16; \
	./xmlchange NTASKS_CPL=64,NTASKS_ICE=64; \
	./xmlchange ROOTPE_OCN=80; \
	./xmlchange NTASKS_OCN=1536; \
	sed 's/"POP_AUTO_DECOMP" value=".*"/"POP_AUTO_DECOMP" value="false"/g' env_build.xml > env_build.xml.$$; \
	mv env_build.xml.$$ env_build.xml; \
	./xmlchange POP_BLCKX=8,POP_BLCKY=4,POP_NX_BLOCKS=64,POP_NY_BLOCKS=32,POP_MXBLCKS=2,POP_DECOMPTYPE=spacecurve; \
	./case.setup

run:
	@echo 'Running ${ACTION}'
	cp -f ${INCDIR}/runcase ${WORKDIR}/${ACTION}/case
	mkdir -p ${WORKDIR}/${ACTION}/output
	cd ${WORKDIR}/${ACTION}/output; ${KGEN}/bin/kgen \
		--cmd-clean "cd ${WORKDIR}/${ACTION}/case; ./case.build --clean" \
		--cmd-build "cd ${WORKDIR}/${ACTION}/case; ./case.build" \
		--cmd-run "cd ${WORKDIR}/${ACTION}/case; ./runcase" \
		-e "${INCDIR}/exclude.ini" \
		--outdir ${WORKDIR}/${ACTION}/output \
		--state-switch type=copy,directory=${WORKDIR}/${ACTION}/case/SourceMods/src.pop,clean="rm -f /glade/scratch/youngsun/cylcworkspace/pop/coverage/case/SourceMods/src.pop/*" \
		--timing repeat=10 \
		--mpi enable \
		--openmp enable \
		${WORKDIR}/${ACTION}/src/${CALLSITE}
