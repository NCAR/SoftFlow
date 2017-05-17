# Wrapper for useful commands

###############
# Variables
##############

TEST ?= perfTest
CPU ?= BDW
HOMME_VER := 28

HOMME_CONTROL := /glade/u/home/youngsun/apps/homme/ipcc02
HOMME_EXPERIMENT := /glade/u/home/youngsun/apps/homme/dungeon${HOMME_VER}

MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SUITENAME := $(shell python -c "print '_'.join('${MAKEFILEDIR}'.split('workflow')[1].split('/')[:-1])")
WORKDIR := /glade/scratch/youngsun/cylcworkspace/${SUITENAME}_${TEST}_${CPU}

BINDIR := ${MAKEFILEDIR}
SUITEDIR := ${MAKEFILEDIR}/..
SOFTFLOWDIR := ${SUITEDIR}/../../../../lib/python
INCDIR := ${SUITEDIR}/inc
PYTHONDIR := ${SUITEDIR}/lib/python:${SOFTFLOWDIR}
CGROUPDIR := ${WORKDIR}/cgroup
EGROUPDIR := ${WORKDIR}/egroup
#DATADIR := ${WORKDIR}/data

EXTRAE_HOME ?= /glade/p/tdd/asap/contrib/extrae/3.3.0
#EXTRAE_HOME ?= /glade/p/tdd/asap/contrib/extrae/3.4.3
FOLDING_HOME ?= /glade/p/tdd/asap/contrib/folding/

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

cylc_log:
	cylc log ${SUITENAME}

cylc_stderr:
	cylc log -e ${SUITENAME} ${TASKID}

cylc_stdout:
	cylc log -o ${SUITENAME} ${TASKID}

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

copy_control:
	@echo 'Begin copy_control'
	mkdir -p ${CGROUPDIR}/homme
	cp -R -u -p ${HOMME_CONTROL}/* ${CGROUPDIR}/homme
	cp -f ${INCDIR}/prim_main.F90.control ${CGROUPDIR}/homme/src/prim_main.F90
	cp -f ${INCDIR}/FindExtrae.cmake ${CGROUPDIR}/homme/cmake
	cp -f ${INCDIR}/HommeMacros.cmake.control ${CGROUPDIR}/homme/cmake/HommeMacros.cmake

copy_experiment:
	@echo 'Begin copy_experiment'
	mkdir -p ${EGROUPDIR}/homme
	cp -R -u -p ${HOMME_EXPERIMENT}/* ${EGROUPDIR}/homme
	cp -f ${INCDIR}/prim_main.F90.experiment.${HOMME_VER} ${EGROUPDIR}/homme/src/prim_main.F90
	cp -f ${INCDIR}/prim_advection_mod.F90.experiment.${HOMME_VER} ${EGROUPDIR}/homme/src/share/prim_advection_mod.F90
	cp -f ${INCDIR}/FindExtrae.cmake ${EGROUPDIR}/homme/cmake
	cp -f ${INCDIR}/HommeMacros.cmake.experiment ${EGROUPDIR}/homme/cmake/HommeMacros.cmake

config_control:
	@echo 'Begin config_control'
	mkdir -p ${CGROUPDIR}/build
	cd ${CGROUPDIR}/build; rm -rf CMakeFiles CMakeCache.txt
	cd ${CGROUPDIR}/build; cmake \
		-C ${INCDIR}/yellowstoneIntel.cmake \
        -DHOMME_PROJID=NONE \
        -DENABLE_PERFTEST=TRUE \
        -DEXTRAE_LIB=mpitracef \
		-DENABLE_OPENMP=FALSE \
        -DEXTRAE_DIR:PATH=${EXTRAE_HOME} \
		${CGROUPDIR}/homme

        #-DCMAKE_Fortran_COMPILER=mpif90 \
        #-DCMAKE_C_COMPILER=icc \
        #-DCMAKE_CXX_COMPILER=icpc \
        #-DNETCDF_DIR:PATH=${NETCDF_DIR} \
        #-DHDF5_DIR:PATH= ${HDF5_DIR} \

        #-DENABLE_OPENMP=TRUE \
        #-DEXTRAE_DIR:PATH=/global/homes/g/grnydawn/opt/extrae/3.4.1 \

config_experiment:
	@echo 'Begin config_experiment'
	mkdir -p ${EGROUPDIR}/build
	cd ${EGROUPDIR}/build; rm -rf CMakeFiles CMakeCache.txt
	cd ${EGROUPDIR}/build; cmake \
		-C ${INCDIR}/yellowstoneIntel.cmake \
        -DHOMME_PROJID=NONE \
        -DENABLE_PERFTEST=TRUE \
        -DEXTRAE_LIB=mpitracef \
		-DENABLE_OPENMP=FALSE \
        -DEXTRAE_DIR:PATH=${EXTRAE_HOME} \
		${EGROUPDIR}/homme

        #-DCMAKE_Fortran_COMPILER=ftn \
        #-DCMAKE_C_COMPILER=cc \
        #-DCMAKE_CXX_COMPILER=CC \
        #-DNETCDF_DIR:PATH=${NETCDF_DIR} \
        #-DHDF5_DIR:PATH= ${HDF5_DIR} \

        #-DEXTRAE_DIR:PATH=/global/homes/g/grnydawn/opt/extrae/3.4.1 \
		#-DADD_Fortran_FLAGS="-L${EXTRAE_HOME}/lib -l mpitracef" \
		#-DADD_Fortran_FLAGS="-L${EXTRAE_HOME}/lib -l mpitracef" \

clean_control:
	@echo 'Begin clean_control'
	cd ${CGROUPDIR}/build; make clean

clean_experiment:
	@echo 'Begin clean_experiment'
	cd ${EGROUPDIR}/build; make clean

build_control:
	@echo 'Begin build_control'
	cd ${CGROUPDIR}/build; make VERBOSE=1 -j 8 ${TEST}
	cp -f ${INCDIR}/prim_main.F90.orig.control ${CGROUPDIR}/homme/src/prim_main.F90

build_experiment:
	@echo 'Begin build_experiment'
	cd ${EGROUPDIR}/build; make VERBOSE=1 -j 8 ${TEST}
	cp -f ${INCDIR}/prim_main.F90.orig.experiment.${HOMME_VER} ${EGROUPDIR}/homme/src/prim_main.F90

run_control:
	@echo 'Begin run_control'
	mkdir -p ${CGROUPDIR}/run/movies
	cp -f ${INCDIR}/extrae.xml ${CGROUPDIR}/run
	cd ${CGROUPDIR}/run; \
		mkdir -p ${CGROUPDIR}/build/tests/${TEST}/vcoord; \
		rm -f vcoord; ln -s ${CGROUPDIR}/build/tests/${TEST}/vcoord vcoord; \
		cp -f ${INCDIR}/*.ascii vcoord; \
		rm -f ${TEST}.nl; cp ${INCDIR}/${TEST}.nl ${TEST}.nl; \
        sed "s,EXECUTABLE,${CGROUPDIR}/build/test_execs/${TEST}/${TEST},g" ${BINDIR}/job.${CPU}.submit | \
		sed "s,NAMELIST,${TEST}.nl,g" > ./job.${CPU}.submit; \
        bsub -K < ./job.${CPU}.submit

run_experiment:
	@echo 'Begin run_experiment'
	mkdir -p ${EGROUPDIR}/run/movies
	cp -f ${INCDIR}/extrae.xml ${EGROUPDIR}/run
	cd ${EGROUPDIR}/run; \
		rm -f vcoord; ln -s ${EGROUPDIR}/build/tests/${TEST}/vcoord vcoord; \
		rm -f ${TEST}.nl; cp ${INCDIR}/${TEST}.nl ${TEST}.nl; \
        sed "s,EXECUTABLE,${EGROUPDIR}/build/test_execs/${TEST}/${TEST},g" ${BINDIR}/job.${CPU}.submit | \
		sed "s,NAMELIST,${TEST}.nl,g" > ./job.${CPU}.submit; \
        bsub -K < ./job.${CPU}.submit

collect_control:
	@echo 'Begin collect_control'
	cd ${CGROUPDIR}/run; \
	${EXTRAE_HOME}/bin/mpi2prv -f TRACE.mpits -o ${TEST}.prv; \
	tar -cvf ${TEST}_control${SUITENAME}.tar ${TEST}.prv ${TEST}.pcf ${TEST}.row


collect_experiment:
	@echo 'Begin collect_experiment'
	cd ${EGROUPDIR}/run; \
	${EXTRAE_HOME}/bin/mpi2prv -f TRACE.mpits -o ${TEST}.prv; \
	tar -cvf ${TEST}_experiment${SUITENAME}.tar ${TEST}.prv ${TEST}.pcf ${TEST}.row
