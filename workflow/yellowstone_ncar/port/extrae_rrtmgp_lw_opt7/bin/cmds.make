# Wrapper for useful commands

###############
# Variables
##############

CPU ?= SNB

CONTROL_SRCDIR := /glade/p/tdd/asap/kgen_kernels/port/rrtmgp14_cam5_4_48/rrtmgp_lw.v3
MIDDLESTAGE_SRCDIR := /glade/p/tdd/asap/kgen_kernels/port/rrtmgp14_cam5_4_48/rrtmgp_lw.v6
EXPERIMENT_SRCDIR := /glade/p/tdd/asap/kgen_kernels/port/rrtmgp14_cam5_4_48/rrtmgp_lw.v7

MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SUITENAME := $(shell python -c "print '_'.join('${MAKEFILEDIR}'.split('workflow')[1].split('/')[:-1])")
WORKDIR := /glade/scratch/youngsun/cylcworkspace/${SUITENAME}

BINDIR := ${MAKEFILEDIR}
SUITEDIR := ${MAKEFILEDIR}/..
SOFTFLOWDIR := ${SUITEDIR}/../../../../lib/python
INCDIR := ${SUITEDIR}/inc
PYTHONDIR := ${SUITEDIR}/lib/python:${SOFTFLOWDIR}
CGROUPDIR := ${WORKDIR}/cgroup
MGROUPDIR := ${WORKDIR}/mgroup
EGROUPDIR := ${WORKDIR}/egroup
#DATADIR := ${WORKDIR}/data

EXTRAE_HOME ?= /glade/p/tdd/asap/contrib/extrae/3.3.0
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

bsub:
	bsub -XF -Is -q caldera -W 20:00 -n 16 -P STDD0002 /bin/bash

####################
# Cylc Suite Targets
####################

preprocess:
	@echo 'Begin preprocess'

copy_control:
	@echo 'Begin copy_control'
	mkdir -p ${CGROUPDIR}
	cp -R -p ${CONTROL_SRCDIR}/* ${CGROUPDIR}
	cp -f ${INCDIR}/extrae.xml ${CGROUPDIR}/kernel
	cp -f ${INCDIR}/mo_rrtmgp_lw.F90.v3 ${CGROUPDIR}/kernel/mo_rrtmgp_lw.F90
	cp -f ${INCDIR}/radiation.F90.v3 ${CGROUPDIR}/kernel/radiation.F90
	cp -f ${INCDIR}/Makefile.v3 ${CGROUPDIR}/kernel/Makefile

copy_middlestage:
	@echo 'Begin copy_middlestage'
	mkdir -p ${MGROUPDIR}
	cp -R -p ${MIDDLESTAGE_SRCDIR}/* ${MGROUPDIR}
	cp -f ${INCDIR}/extrae.xml ${MGROUPDIR}/kernel
	cp -f ${INCDIR}/mo_rrtmgp_lw.F90.v6 ${MGROUPDIR}/kernel/mo_rrtmgp_lw.F90
	cp -f ${INCDIR}/radiation.F90.v6 ${MGROUPDIR}/kernel/radiation.F90
	cp -f ${INCDIR}/Makefile.v6 ${MGROUPDIR}/kernel/Makefile

copy_experiment:
	@echo 'Begin copy_experiment'
	mkdir -p ${EGROUPDIR}
	cp -R -p ${EXPERIMENT_SRCDIR}/* ${EGROUPDIR}
	cp -f ${INCDIR}/extrae.xml ${EGROUPDIR}/kernel
	cp -f ${INCDIR}/mo_rrtmgp_lw.F90.v6 ${EGROUPDIR}/kernel/mo_rrtmgp_lw.F90
	cp -f ${INCDIR}/radiation.F90.v6 ${EGROUPDIR}/kernel/radiation.F90
	cp -f ${INCDIR}/Makefile.v7 ${EGROUPDIR}/kernel/Makefile

clean_control:
	@echo 'Begin clean_control'
	cd ${CGROUPDIR}/kernel; make clean

clean_middlestage:
	@echo 'Begin clean_middlestage'
	cd ${MGROUPDIR}/kernel; make clean

clean_experiment:
	@echo 'Begin clean_experiment'
	cd ${EGROUPDIR}/kernel; make clean

build_control:
	@echo 'Begin build_control'
	cd ${CGROUPDIR}/kernel; make -j 4 build

build_middlestage:
	@echo 'Begin build_middlestage'
	cd ${MGROUPDIR}/kernel; make -j 4 build

build_experiment:
	@echo 'Begin build_experiment'
	cd ${EGROUPDIR}/kernel; make -j 4 build

run_control:
	@echo 'Begin run_control'
	cd ${CGROUPDIR}/kernel; \
		sed "s,EXECUTABLE,${CGROUPDIR}/kernel/kernel.exe,g" ${BINDIR}/job.${CPU}.submit > ./job.${CPU}.submit; \
		bsub -K < ./job.${CPU}.submit

run_middlestage:
	@echo 'Begin run_middlestage'
	cd ${MGROUPDIR}/kernel; \
		sed "s,EXECUTABLE,${MGROUPDIR}/kernel/kernel.exe,g" ${BINDIR}/job.${CPU}.submit > ./job.${CPU}.submit; \
		bsub -K < ./job.${CPU}.submit

run_experiment:
	@echo 'Begin run_experiment'
	cd ${EGROUPDIR}/kernel; \
		sed "s,EXECUTABLE,${EGROUPDIR}/kernel/kernel.exe,g" ${BINDIR}/job.${CPU}.submit > ./job.${CPU}.submit; \
		bsub -K < ./job.${CPU}.submit

collect_control:
	@echo 'Begin collect_control'
	cd ${CGROUPDIR}/kernel; \
	${EXTRAE_HOME}/bin/mpi2prv -f TRACE.mpits -o control.prv; \
	tar -cvf control${SUITENAME}.tar control.prv control.pcf control.row

collect_middlestage:
	@echo 'Begin collect_middlestage'
	cd ${MGROUPDIR}/kernel; \
	${EXTRAE_HOME}/bin/mpi2prv -f TRACE.mpits -o middlestage.prv; \
	tar -cvf middlestage${SUITENAME}.tar middlestage.prv middlestage.pcf middlestage.row

collect_experiment:
	@echo 'Begin collect_experiment'
	cd ${EGROUPDIR}/kernel; \
	${EXTRAE_HOME}/bin/mpi2prv -f TRACE.mpits -o experiment.prv; \
	tar -cvf experiment${SUITENAME}.tar experiment.prv experiment.pcf experiment.row
