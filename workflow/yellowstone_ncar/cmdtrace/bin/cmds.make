# Wrapper for useful commands

###############
# Variables
##############

CPU ?= SNB

MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SUITENAME := $(shell python -c "print '_'.join('${MAKEFILEDIR}'.split('workflow')[1].split('/')[:-1])")
WORKDIR := /glade/scratch/youngsun/cylcworkspace/${SUITENAME}

BINDIR := ${MAKEFILEDIR}
SUITEDIR := ${MAKEFILEDIR}/..
SOFTFLOWDIR := ${SUITEDIR}/../../../../lib/python
INCDIR := ${SUITEDIR}/inc
SRCDIR := ${SUITEDIR}/src
TESTDIR := ${SUITEDIR}/test
PYTHONDIR := ${SUITEDIR}/lib/python:${SOFTFLOWDIR}

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

copy:
	@echo 'Begin copy'
	mkdir -p ${WORKDIR}/example
	cp -f ${INCDIR}/Makefile ${WORKDIR}/example
	cp -f ${INCDIR}/test_top.F90 ${WORKDIR}/example
	cp -f ${INCDIR}/calling_module.F90 ${WORKDIR}/example
	cp -f ${INCDIR}/kernel.F90 ${WORKDIR}/example
	mkdir -p ${WORKDIR}/src
	cp -f ${SRCDIR}/Makefile ${WORKDIR}/src
	mkdir -p ${WORKDIR}/test
	cp -f ${TESTDIR}/test_cmdtrace.py ${WORKDIR}/test

build_cmdtrace:
	@echo 'Begin building cmdtrace'
	mkdir -p ${WORKDIR}/src
	cd ${SRCDIR}; make

run_test:
	@echo 'Begin testing'
	cd ${WORKDIR}/test; python test_cmdtrace.py
