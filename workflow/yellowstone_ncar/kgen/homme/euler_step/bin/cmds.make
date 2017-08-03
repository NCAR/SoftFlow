# Wrapper for useful commands

###############
# Variables
##############

TEST := perfTest
CPU := SNB

HOMME := /glade/u/home/youngsun/apps/homme/dungeon28

MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SUITENAME := $(shell python -c "print '_'.join('${MAKEFILEDIR}'.split('workflow')[1].split('/')[:-1])")
WORKDIR := /glade/scratch/youngsun/cylcworkspace/${SUITENAME}_${TEST}_${CPU}

BINDIR := ${MAKEFILEDIR}
SUITEDIR := ${MAKEFILEDIR}/..
SOFTFLOWDIR := ${SUITEDIR}/../../../../lib/python
INCDIR := ${SUITEDIR}/inc
PYTHONDIR := ${SUITEDIR}/lib/python:${SOFTFLOWDIR}

KGEN := /glade/u/home/youngsun/repos/github/KGen
CALLSITE :=  components/cam/src/physics/cam/micro_mg_cam.F90:micro_mg_cam:micro_mg_cam_tend:micro_mg_get_cols2_0

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

salloc:
	salloc -N 1 -C haswell -p regular --qos=premium -t 08:00:00 -L SCRATCH

####################
# Cylc Suite Targets
####################

#preprocess => copy => config => clean => build => run => collect

preprocess:
	@echo 'Begin preprocess'

copy:
	@echo 'Begin copy'
	mkdir -p ${WORKDIR}/homme
	cp -R -p ${HOMME}/* ${WORKDIR}/homme

config:
	@echo 'Begin config'
	mkdir -p ${WORKDIR}/build
	cd ${WORKDIR}/build; rm -rf CMakeFiles CMakeCache.txt
	cd ${WORKDIR}/build; cmake \
		-C ${INCDIR}/yellowstoneIntel.cmake \
		-DHOMME_PROJID=STDD0002 \
        -DENABLE_PERFTEST=TRUE \
		-DENABLE_OPENMP=FALSE \
		${WORKDIR}/homme

clean:
	@echo 'Begin clean'
	cd ${WORKDIR}/build; make clean

#build:
#	@echo 'Begin build'
#	cd ${WORKDIR}/build; make -j 8 ${TEST}

bsub -K -env EXEC=${WORKDIR}/build/src/preqx/preqx,NAMELIST=./test_ne8.nl < ${BINDIR}/job.${CPU}.submit


run:
	@echo 'Begin run'
	mkdir -p ${WORKDIR}/run/movies
	cd ${WORKDIR}/run; \
		mkdir -p ${WORKDIR}/build/tests/${TEST}/vcoord; \
		rm -f vcoord; ln -s ${WORKDIR}/build/tests/${TEST}/vcoord vcoord; \
		cp -f ${INCDIR}/*.ascii vcoord; \
		rm -f ${TEST}.nl; cp ${INCDIR}/${TEST}.nl ${TEST}.nl
        sed "s,EXECUTABLE,${WORKDIR}/build/test_execs/${TEST}/${TEST},g" ${BINDIR}/job.${CPU}.submit | \
        sed "s,NAMELIST,${TEST}.nl,g" > ./job.${CPU}.submit; \
	cd ${WORKDIR}/run; ${KGEN}/bin/kgen \
        --cmd-clean "cd ${WORKDIR}/build; ./make clean" \
        --cmd-build "cd ${WORKDIR}/build; ./make -j 8 ${TEST}" \
        --cmd-run "cd ${WORKDIR}/run; bsub -K < ./job.${CPU}.submit" \
        --outdir ${WORKDIR}/run \
        --intrinsic skip,except=shr_spfn_mod:shr_spfn_gamma_nonintrinsic_r8:sum \
        --skip coverage \
        --mpi comm=mpicom,use="spmd_utils:mpicom" \
        --state-switch type=copy,directory=${WORKDIR}/case/SourceMods/src.cam,clean="rm -f ${WORKDIR}/case/SourceMods/src.cam/*" \
        --source alias=/glade2/scratch2:/glade/scratch \
        --timing repeat=10 \
        --mpi enable \
        --openmp enable \
        ${WORKDIR}/src/${CALLSITE}

        #sed "s,EXECUTABLE,${WORKDIR}/build/test_execs/${TEST}/${TEST},g" ${BINDIR}/job.${CPU}.submit | \
		#sed "s,NAMELIST,${TEST}.nl,g" > ./job.${CPU}.submit; \
        #bsub -K < ./job.${CPU}.submit

collect:
	@echo 'Begin collect'
