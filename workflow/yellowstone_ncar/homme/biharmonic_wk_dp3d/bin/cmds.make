# Wrapper for useful commands

###############
# Variables
##############

SUITENAME := extrae
TEST := perfTest
CPU := SNB

HOMME := /global/homes/g/grnydawn/apps/homme_dungeon15_hsw_nggps/dungeon

WORKDIR := ${CSCRATCH}/cylcworkspace/${SUITENAME}_${CPU}
MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
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

preprocess:
	@echo 'Begin preprocess'

copy:
	@echo 'Begin copy'
	mkdir -p ${WORKDIR}/homme
	cp -R -u -p ${HOMME}/* ${WORKDIR}/homme
	cp -f ${INCDIR}/prim_main.F90 ${WORKDIR}/homme/src/prim_main.F90
	cp -f ${INCDIR}/prim_advection_mod.F90 ${WORKDIR}/homme/src/share
	cp -f ${INCDIR}/FindExtrae.cmake ${WORKDIR}/homme/cmake
	cp -f ${INCDIR}/HommeMacros.cmake ${WORKDIR}/homme/cmake
	cp -f ${INCDIR}/extrae.xml ${WORKDIR}/run

config:
	@echo 'Begin config'
	mkdir -p ${WORKDIR}/build
	cd ${WORKDIR}/build; rm -rf CMakeFiles CMakeCache.txt
	cd ${WORKDIR}/build; cmake \
        -DCMAKE_Fortran_COMPILER=ftn \
        -DCMAKE_C_COMPILER=cc \
        -DCMAKE_CXX_COMPILER=CC \
        -DNETCDF_DIR:PATH=${NETCDF_DIR} \
        -DHDF5_DIR:PATH= ${HDF5_DIR} \
        -DHOMME_PROJID=NONE \
        -DENABLE_PERFTEST=TRUE \
        -DEXTRAE_LIB=mpitracef \
		${WORKDIR}/homme

        #-DENABLE_OPENMP=TRUE \
        #-DEXTRAE_DIR:PATH=/global/homes/g/grnydawn/opt/extrae/3.4.1 \
#
#clean:
#	@echo 'Begin clean'
#	cd ${WORKDIR}/build; make clean
#
#build:
#	@echo 'Begin build'
#	cd ${WORKDIR}/build; make VERBOSE=1 -j 8 ${TEST}
#	cp -f ${INCDIR}/prim_main.F90.orig ${WORKDIR}/homme/src/prim_main.F90

run:
	@echo 'Begin run'
	mkdir -p ${WORKDIR}/run/movies
	cd ${WORKDIR}/run; \
		rm -f vcoord; ln -s ${WORKDIR}/build/tests/${TEST}/vcoord vcoord; \
		rm -f ${TEST}.nl; cp ${WORKDIR}/build/tests/${TEST}/${TEST}.nl ${TEST}.nl; \
		sbatch -W ${BINDIR}/job.${CPU}.submit ${WORKDIR}/build/test_execs/${TEST}/${TEST} ${TEST}.nl
