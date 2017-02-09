# Job commands
# Cylc should issue commands in this Makefile

###############
# Variables
##############

CPU ?= KNL
SFROOTDIR ?= ${HOME}/repos/github/SoftFlow
CYLC_SUITE_REG_NAME ?= chemck
CYLC_SUITE_DEF_PATH ?= ${SFROOTDIR}/workflow/hpcfl_ncar/dspo/chemck

WORKDIR := /lustre/scratch/youngsun/cylcworkspace/${CYLC_SUITE_REG_NAME}_${CPU}
CGROUPDIR := ${WORKDIR}/cgroup
EGROUPDIR := ${WORKDIR}/egroup
BINDIR := ${CYLC_SUITE_DEF_PATH}/bin
INCDIR := ${CYLC_SUITE_DEF_PATH}/inc


###############
# Cylc commands
###############

register:
	cylc register ${CYLC_SUITE_REG_NAME} ${CYLC_SUITE_DEF_PATH}

validate:
	cylc validate ${CYLC_SUITE_REG_NAME}

stop:
	cylc stop ${CYLC_SUITE_REG_NAME}

ready:
	cylc reset -s ready ${CYLC_SUITE_REG_NAME} ${TASKID}

run:
	cylc run ${CYLC_SUITE_REG_NAME}

monitor:
	cylc monitor ${CYLC_SUITE_REG_NAME}

rmport:
	rm -f ${HOME}/.cylc/ports/${CYLC_SUITE_REG_NAME}

###############
# Task commands
###############

preprocess:
	python ${SFROOTDIR}/lib/python/packresult.py init

copyfiles:
	mkdir -p ${WORKDIR}/cgroup
	mkdir -p ${WORKDIR}/egroup
	mkdir -p ${WORKDIR}/data
	yes | cp -fp ${CYLC_SUITE_DEF_PATH}/src/* ${WORKDIR}/cgroup
	yes | cp -fp ${CYLC_SUITE_DEF_PATH}/src/* ${WORKDIR}/egroup
	yes | cp -fp ${CYLC_SUITE_DEF_PATH}/../chemv4/data/* ${WORKDIR}/data
	yes | cp -fp ${INCDIR}/Makefile-cgroup ${WORKDIR}/cgroup
	yes | cp -fp ${INCDIR}/Makefile-egroup ${WORKDIR}/egroup
	#mv -f ${WORKDIR}/egroup/mo_nln_matrix.F90 ${WORKDIR}/egroup/mo_nln_matrix.F90.bak
	#yes | cp -fp ${INCDIR}/mo_nln_matrix.F90-egroup ${WORKDIR}/egroup/mo_nln_matrix.F90

bldcontrol:
	source ${HOME}/intel.compiler; cd ${CGROUPDIR}; \
		make -j 4 -f ./Makefile-cgroup build CPU=${CPU}; \
		python ${SFROOTDIR}/lib/python/packresult.py set replace compiler-version `ifort -v 2>&1`

bldexp:
	source ${HOME}/intel.compiler; cd ${EGROUPDIR}; \
		make -j 4 -f ./Makefile-egroup build CPU=${CPU}; \
		python ${SFROOTDIR}/lib/python/packresult.py set replace compiler-version `ifort -v 2>&1`

runcontrol:
ifeq (${CPU},KNL)
	source ${HOME}/intel.compiler; ulimit -s unlimited; cd ${CGROUPDIR}; srun -n 1 numactl --membind=1 ./kernel.exe
else
	source ${HOME}/intel.compiler; ulimit -s unlimited; cd ${CGROUPDIR}; srun -n 1 ./kernel.exe
endif
	python ${SFROOTDIR}/lib/python/packresult.py set replace tasks##${CYLC_TASK_ID}##cpu \
		`cat /proc/cpuinfo | grep model | grep name | head -n 1 | cut -d ":" -f 2`
	python ${SFROOTDIR}/lib/python/packresult.py set replace tasks##${CYLC_TASK_ID}##node `uname -n`

runexp:
ifeq (${CPU},KNL)
	source ${HOME}/intel.compiler; ulimit -s unlimited; cd ${EGROUPDIR}; srun -n 1 numactl --membind=1 ./kernel.exe
else
	source ${HOME}/intel.compiler; ulimit -s unlimited; cd ${EGROUPDIR}; srun -n 1 ./kernel.exe
endif
	python ${SFROOTDIR}/lib/python/packresult.py set replace tasks##${CYLC_TASK_ID}##cpu \
		`cat /proc/cpuinfo | grep model | grep name | head -n 1 | cut -d ":" -f 2`
	python ${SFROOTDIR}/lib/python/packresult.py set replace tasks##${CYLC_TASK_ID}##node `uname -n`

checkdiff:
	python ${BINDIR}/statdiff.py ${BASELINE} ${FOLLOWUP} ${CPU} \
		$(shell python ${SFROOTDIR}/lib/python/packresult.py outfile) ${CYLC_SUITE_REG_NAME}

genoutput:
	python ${SFROOTDIR}/lib/python/packresult.py pack
