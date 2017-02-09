# Makefile for HOMME project

# User-providing information
SVNTAG ?= https://svn-homme-model.cgd.ucar.edu/branch_tags/dungeon_tags/dungeon16
TEST   ?= perfTest

# Modify if following information is not matched with new test
HOMME_EXE := ${BUILDDIR}/test_execs/${TEST}/${TEST}
NAMELIST  := ${BUILDDIR}/tests/${TEST}/${TEST}.nl
VCOORD    := ${BUILDDIR}/tests/${TEST}/vcoord

# directories
WORKDIR ?= ${CSCRATCH}/homme
INSTALLDIR := ${WORKDIR}/install
BUILDDIR := ${WORKDIR}/build
RUNDIR := ${WORKDIR}/run
CURDIR := ${PWD}

check:
	# module load cray-hdf5/1.10.0
	# module load cray-netcdf
	@echo cc = `cc --version`
	@echo CC = `CC --version`
	@echo ftn = `ftn --version`
	@echo NETCDF_DIR = ${NETCDF_DIR}
	@echo HDF5_DIR = ${HDF5_DIR}

install:
	echo "Press enter if password is requested and then input username and password."
	mkdir -p ${INSTALLDIR}
	svn co ${SVNTAG} ${INSTALLDIR}

config:
	mkdir -p ${BUILDDIR}
	rm -rf ${BUILDDIR}/CMakeFiles ${BUILDDIR}/CMakeCache.txt
	cd ${BUILDDIR}; cmake \
		-DCMAKE_Fortran_COMPILER=ftn \
		-DCMAKE_C_COMPILER=cc \
		-DCMAKE_CXX_COMPILER=CC \
		-DNETCDF_DIR:PATH=${NETCDF_DIR} \
		-DHDF5_DIR:PATH= ${HDF5_DIR} \
		-DHOMME_PROJID=NONE \
		-DENABLE_PERFTEST=TRUE \
		-DENABLE_OPENMP=TRUE \
		${INSTALLDIR}

build:
	mkdir -p ${BUILDDIR}
	cd ${BUILDDIR}; make -j 4 ${TEST}

run:
	mkdir -p ${RUNDIR}/movies
	cd ${RUNDIR}; rm -f vcoord; ln -s ${VCOORD} vcoord
	cd ${RUNDIR}; rm -f ${TEST}.nl; cp ${NAMELIST} ${TEST}.nl
	cd ${RUNDIR}; sbatch ${CURDIR}/job.submit ${HOMME_EXE} ${TEST}.nl
