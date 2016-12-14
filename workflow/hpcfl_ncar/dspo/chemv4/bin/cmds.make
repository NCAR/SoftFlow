# Wrapper for useful commands

###############
# Variables
##############

SUITENAME := chemv4
WORKDIR := /lustre/scratch/youngsun/dspowork
KERNELREPO := https://github.com/NCAR/kernelOptimization
CHEMV4 := all/WACCM_imp_sol_vector/v04
CHEMDATA := all/WACCM_imp_sol_vector/data
MAKEFILEDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

###########
# Targets
###########

register:
	cylc register ${SUITENAME} ${MAKEFILEDIR}/..

validate:
	cylc validate ${SUITENAME}

stop:
	cylc stop ${SUITENAME}

copyfiles:
	rm -rf ${WORKDIR}
	mkdir -p ${WORKDIR}
	cd ${WORKDIR}; svn export --force ${KERNELREPO}/trunk/${CHEMV4} ${WORKDIR}/${SUITENAME}/cgroup
	cd ${WORKDIR}; svn export --force ${KERNELREPO}/trunk/${CHEMDATA} ${WORKDIR}/${SUITENAME}/data
	cp -rf ${WORKDIR}/${SUITENAME}/cgroup ${WORKDIR}/${SUITENAME}/egroup
