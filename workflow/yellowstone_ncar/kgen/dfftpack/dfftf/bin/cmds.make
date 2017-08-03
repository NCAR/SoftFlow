# Wrapper for useful commands

###############
# Variables
##############

KGEN := /glade/u/home/youngsun/repos/github/KGen

MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SUITENAME := $(shell python -c "print '_'.join('${MAKEFILEDIR}'.split('workflow')[1].split('/')[:-1])")
WORKDIR := /glade/scratch/youngsun/cylcworkspace/${SUITENAME}

SUITEDIR := ${MAKEFILEDIR}/..
INCDIR := ${SUITEDIR}/inc

CALLSITE :=  test.f

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
	@echo 'Copying DFFTPACK Test Program'
	mkdir -p ${WORKDIR}/src
	rm -rf ${WORKDIR}/src/*
	cp -R -p -f ${INCDIR}/* ${WORKDIR}/src

run:
	@echo 'Running KGEN' 
	mkdir -p ${WORKDIR}/output
	cd ${WORKDIR}/output; ${KGEN}/bin/kgen \
		--cmd-clean "cd ${WORKDIR}/src; make clean" \
		--cmd-build "cd ${WORKDIR}/src; make build" \
		--cmd-run "cd ${WORKDIR}/src; make run" \
		--outdir ${WORKDIR}/output \
		--skip coverage \
		--source format=fixed \
		--add-mpi-frame np=2,mpiexec=mpirun \
		--timing repeat=1 \
		--repr-etime timer=cputime \
		${WORKDIR}/src/${CALLSITE}

		#--repr-etime minval=1.0E-7,maxval=2.0E-5 \
