# Wrapper for useful commands

###############
# Variables
##############

TEST := perfTest
CPU ?= HSW

#HOMME_CONTROL := /global/homes/g/grnydawn/apps/homme_dungeon15_hsw_nggps/dungeon
#HOMME_EXPERIMENT := /global/homes/g/grnydawn/apps/homme_dungeon16_hsw_perfTest/dungeon

HOMME_CONTROL := ${HOME}/apps/homme_ipcc02
HOMME_EXPERIMENT := ${HOME}/apps/homme_dungeon28

MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SUITENAME := $(shell python -c "print '_'.join('${MAKEFILEDIR}'.split('workflow')[1].split('/')[:-1])")
WORKDIR := ${CSCRATCH}/cylcworkspace/${SUITENAME}_${CPU}

BINDIR := ${MAKEFILEDIR}
SUITEDIR := ${MAKEFILEDIR}/..
SOFTFLOWDIR := ${SUITEDIR}/../../../..
INCDIR := ${SUITEDIR}/inc
PYTHONDIR := ${SUITEDIR}/lib/python:${SOFTFLOWDIR}/lib/python
CGROUPDIR := ${WORKDIR}/cgroup
EGROUPDIR := ${WORKDIR}/egroup
#DATADIR := ${WORKDIR}/data

EXTRAE_HOME := /global/homes/g/grnydawn/opt/extrae/3.4.1
FOLDING_HOME := /global/homes/g/grnydawn/opt/folding/1.0.2

CFOLDING := ${CGROUPDIR}/run/${TEST}:ipcc02
EFOLDING := ${EGROUPDIR}/run/${TEST}:dungeon28

PLOT_SCRIPT_EXFOLD ?= ${SOFTFLOWDIR}/lib/python/plot_exfold.py
PLOT_SCRIPT_EXFILL ?= ${SOFTFLOWDIR}/lib/python/plot_fill_exfold.py

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

preprocess:
	@echo 'Begin preprocess'

copy_control:
	@echo 'Begin copy_control'
	mkdir -p ${CGROUPDIR}/homme
	cp -R -u -p ${HOMME_CONTROL}/* ${CGROUPDIR}/homme
	cp -f ${INCDIR}/prim_driver_mod.F90.control ${CGROUPDIR}/homme/src/share/prim_driver_mod.F90
	cp -f ${INCDIR}/FindExtrae.cmake ${CGROUPDIR}/homme/cmake
	cp -f ${INCDIR}/HommeMacros.cmake ${CGROUPDIR}/homme/cmake

copy_experiment:
	@echo 'Begin copy_experiment'
	mkdir -p ${EGROUPDIR}/homme
	cp -R -u -p ${HOMME_EXPERIMENT}/* ${EGROUPDIR}/homme
	cp -f ${INCDIR}/prim_driver_mod.F90.experiment ${EGROUPDIR}/homme/src/share/prim_driver_mod.F90
	cp -f ${INCDIR}/prim_advection_mod.F90.experiment ${EGROUPDIR}/homme/src/share/prim_advection_mod.F90
	cp -f ${INCDIR}/FindExtrae.cmake ${EGROUPDIR}/homme/cmake
	cp -f ${INCDIR}/HommeMacros.cmake ${EGROUPDIR}/homme/cmake

config_control:
	@echo 'Begin config_control'
	mkdir -p ${CGROUPDIR}/build
	cd ${CGROUPDIR}/build; rm -rf CMakeFiles CMakeCache.txt
	cd ${CGROUPDIR}/build; cmake \
        -DCMAKE_Fortran_COMPILER=ftn \
        -DCMAKE_C_COMPILER=cc \
        -DCMAKE_CXX_COMPILER=CC \
        -DNETCDF_DIR:PATH=${NETCDF_DIR} \
        -DHDF5_DIR:PATH= ${HDF5_DIR} \
        -DHOMME_PROJID=NONE \
        -DENABLE_PERFTEST=TRUE \
        -DEXTRAE_LIB=mpitracef \
        -DEXTRAE_DIR:PATH=${EXTRAE_HOME} \
		-DADD_Fortran_FLAGS="-g ${INST}" \
		-DOPT_FFLAGS=-O3 \
		${CGROUPDIR}/homme

        #-DENABLE_OPENMP=TRUE \
        #-DEXTRAE_DIR:PATH=/global/homes/g/grnydawn/opt/extrae/3.4.1 \

config_experiment:
	@echo 'Begin config_experiment'
	mkdir -p ${EGROUPDIR}/build
	cd ${EGROUPDIR}/build; rm -rf CMakeFiles CMakeCache.txt
	cd ${EGROUPDIR}/build; cmake \
        -DCMAKE_Fortran_COMPILER=ftn \
        -DCMAKE_C_COMPILER=cc \
        -DCMAKE_CXX_COMPILER=CC \
        -DNETCDF_DIR:PATH=${NETCDF_DIR} \
        -DHDF5_DIR:PATH= ${HDF5_DIR} \
        -DHOMME_PROJID=NONE \
        -DENABLE_PERFTEST=TRUE \
        -DEXTRAE_LIB=mpitracef \
        -DEXTRAE_DIR:PATH=${EXTRAE_HOME} \
		-DADD_Fortran_FLAGS=${INST} \
		-DOPT_FFLAGS=-O3 \
		${EGROUPDIR}/homme

        #-DENABLE_OPENMP=TRUE \
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
	cp -f ${INCDIR}/prim_driver_mod.F90.orig.control ${CGROUPDIR}/homme/src/share/prim_driver_mod.F90

build_experiment:
	@echo 'Begin build_experiment'
	cd ${EGROUPDIR}/build; make VERBOSE=1 -j 8 ${TEST}
	cp -f ${INCDIR}/prim_driver_mod.F90.orig.experiment ${EGROUPDIR}/homme/src/share/prim_driver_mod.F90

run_control:
	@echo 'Begin run_control'
	mkdir -p ${CGROUPDIR}/run/movies
	#cp -f ${INCDIR}/extrae.xml.bursts ${CGROUPDIR}/run/extrae.xml
	cp -f ${INCDIR}/extrae_bursts_1ms.xml ${CGROUPDIR}/run/extrae.xml
	cd ${CGROUPDIR}/run; \
		#rm -f vcoord; ln -s ${CGROUPDIR}/build/tests/${TEST}/vcoord vcoord; \
		rm -rf vcoord; mkdir vcoord; cp ${INCDIR}/*.ascii vcoord; \
		rm -f ${TEST}.nl; cp ${INCDIR}/${TEST}.nl ${TEST}.nl; \
		sbatch -W ${BINDIR}/job.${CPU}.submit ${CGROUPDIR}/build/test_execs/${TEST}/${TEST} ${TEST}.nl

run_experiment:
	@echo 'Begin run_experiment'
	mkdir -p ${EGROUPDIR}/run/movies
	#cp -f ${INCDIR}/extrae.xml.bursts ${EGROUPDIR}/run/extrae.xml
	cp -f ${INCDIR}/extrae_bursts_1ms.xml ${EGROUPDIR}/run/extrae.xml
	cd ${EGROUPDIR}/run; \
		#rm -f vcoord; ln -s ${EGROUPDIR}/build/tests/${TEST}/vcoord vcoord; \
		rm -rf vcoord; mkdir vcoord; cp ${INCDIR}/*.ascii vcoord; \
		rm -f ${TEST}.nl; cp ${INCDIR}/${TEST}.nl ${TEST}.nl; \
		sbatch -W ${BINDIR}/job.${CPU}.submit ${EGROUPDIR}/build/test_execs/${TEST}/${TEST} ${TEST}.nl

collect_control:
	@echo 'Begin collect_control'
	cd ${CGROUPDIR}/run; \
	${EXTRAE_HOME}/bin/mpi2prv -f TRACE.mpits -o ${TEST}.prv; \

collect_experiment:
	@echo 'Begin collect_experiment'
	cd ${EGROUPDIR}/run; \
	${EXTRAE_HOME}/bin/mpi2prv -f TRACE.mpits -o ${TEST}.prv; \

fold_control:
	@echo 'Begin fold_control'
	cd ${CGROUPDIR}/run; \
		${FOLDING_HOME}/bin/folding ./${TEST}.prv "User function"

fold_experiment:
	@echo 'Begin fold_experiment'
	cd ${EGROUPDIR}/run; \
		${FOLDING_HOME}/bin/folding ./${TEST}.prv "User function"

plot:
	@echo 'Begin plot'
	#cd ${WORKDIR}; python ${PLOT_SCRIPT_EXFOLD} -t ${CFOLDING} ${EFOLDING}
	cd ${WORKDIR}; python ${PLOT_SCRIPT_EXFILL} -t -e PAPI_L1_DCM -f compute_and_apply_rhs,euler_step,advance_hypervis_dp ${CFOLDING} ${EFOLDING}
