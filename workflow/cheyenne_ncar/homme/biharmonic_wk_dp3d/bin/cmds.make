# Wrapper for useful commands

###############
# Variables
##############

TEST := preqx
CPU := BDW

SCRATCH=/glade/scratch/youngsun
HOMME := ${HOME}/apps/homme/dungeon20

MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SUITENAME := $(shell python -c "print '_'.join('${MAKEFILEDIR}'.split('workflow')[1].split('/')[:-1])")
WORKDIR := ${SCRATCH}/cylcworkspace/${SUITENAME}_${CPU}

BINDIR := ${MAKEFILEDIR}
SUITEDIR := ${MAKEFILEDIR}/..
SOFTFLOWDIR := ${SUITEDIR}/../../../../lib/python
INCDIR := ${SUITEDIR}/inc
PYTHONDIR := ${SUITEDIR}/lib/python:${SOFTFLOWDIR}
#DATADIR := ${WORKDIR}/data

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

copy:
	@echo 'Begin copy'
	mkdir -p ${WORKDIR}/homme
	cp -R -u -p ${HOMME}/* ${WORKDIR}/homme
	#cp -f ${INCDIR}/prim_main.F90 ${WORKDIR}/homme/src/prim_main.F90
	#cp -f ${INCDIR}/prim_advection_mod.F90 ${WORKDIR}/homme/src/share
	#cp -f ${INCDIR}/FindExtrae.cmake ${WORKDIR}/homme/cmake
	#cp -f ${INCDIR}/HommeMacros.cmake ${WORKDIR}/homme/cmake
	#cp -f ${INCDIR}/extrae.xml ${WORKDIR}/run



config:
	@echo 'Begin config'
	mkdir -p ${WORKDIR}/build
	cd ${WORKDIR}/build; rm -rf CMakeFiles CMakeCache.txt
	cd ${WORKDIR}/build; cmake \
		-DQSIZE_D=10 \
		-DPREQX_PLEV=128 \
		-DPREQX_NP=4 \
		-C ${INCDIR}/yellowstoneIntel.cmake \
		-DHOMME_PROJID=STDD0001 \
		-DENABLE_NANOTIMERS=TRUE \
		-DUSE_BIT64=TRUE \
		-DBUILD_HOMME_PRIM=FALSE \
		-DBUILD_HOMME_SWDGX=FALSE \
		-DBUILD_HOMME_SWEQX=FALSE \
		-DBUILD_HOMME_PRIMDGX=FALSE \
		-DPREQX_USE_ENERGY=FALSE \
		${WORKDIR}/homme

        #-DENABLE_OPENMP=TRUE \
        #-DEXTRAE_DIR:PATH=/global/homes/g/grnydawn/opt/extrae/3.4.1 \

clean:
	@echo 'Begin clean'
	cd ${WORKDIR}/build; make clean

build:
	@echo 'Begin build'
	cd ${WORKDIR}/build; make -j 6 ${TEST}

run:
	@echo 'Begin run'
	mkdir -p ${WORKDIR}/run/movies
	cd ${WORKDIR}/run; \
		rm -rf vcoord; cp -rf ${INCDIR}/vcoord .; \
		rm -f ./test_ne8.nl; cp -f ${INCDIR}/test_ne8.nl .; \
		qsub -W block=true -v EXEC=${WORKDIR}/build/src/preqx/preqx,NAMELIST=./test_ne8.nl ${BINDIR}/job.${CPU}.submit
