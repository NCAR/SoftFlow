# Wrapper for useful commands

###############
# Variables
##############

CESM := /glade/u/home/youngsun/apps/cesm/cesm1_5_beta07
KGEN := /glade/u/home/youngsun/repos/github/KGen

MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SUITENAME := $(shell python -c "print '_'.join('${MAKEFILEDIR}'.split('workflow')[1].split('/')[:-1])")
WORKDIR := /glade/scratch/youngsun/cylcworkspace/cesm/chem_pp

SUITEDIR := ${MAKEFILEDIR}/..
INCDIR := ${SUITEDIR}/inc


CALLSITE :=  components/cam/src/chemistry/mozart/mo_gas_phase_chemdr.F90:mo_gas_phase_chemdr:gas_phase_chemdr:imp_sol

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
	cp -R -u -p ${CESM}/* ${WORKDIR}/src
	#cp ${INCDIR}/createcase ${WORKDIR}/

createcase:
	@echo 'Creating a CESM case'
	rm -rf ${WORKDIR}/case
	cd ${WORKDIR}/src/cime/scripts; ./create_newcase \
		-mach yellowstone \
		-res T62_g16 \
		-compset GECO \
		-case ${WORKDIR}/case \
		-project STDD0002

configcase:
	@echo 'Configuring a CESM case'
	cd ${WORKDIR}/case; \
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
	@echo 'Running KGEN' 
	cp -f ${INCDIR}/runcase ${WORKDIR}/case
	mkdir -p ${WORKDIR}/output
	cd ${WORKDIR}/output; ${KGEN}/bin/kgen \
		--cmd-clean "cd ${WORKDIR}/case; ./case.build --clean" \
		--cmd-build "cd ${WORKDIR}/case; ./case.build" \
		--cmd-run "cd ${WORKDIR}/case; ./runcase" \
		-e "${INCDIR}/exclude.ini" \
		--outdir ${WORKDIR}/output \
		--state-switch type=copy,directory=${WORKDIR}/case/SourceMods/src.pop,clean="rm -f /glade/scratch/youngsun/cylcworkspace/pop/coverage/case/SourceMods/src.pop/*" \
		--timing repeat=10 \
		--mpi enable \
		--openmp enable \
		${WORKDIR}/src/${CALLSITE}
