# This makefile is to help installing Cylc on HPC Future Lab cluster of NCAR.

###########
# Variables
###########

TMPDIR ?= /glade/scratch/youngsun
CYLCTMPDIR := ${TMPDIR}/cylcinstall

CYLC_VERSION := 6.11.2
CYLC_INSTALLDIR := ${HOME}/opt/cylc/${CYLC_VERSION}
CYLC_CMD := $(shell command -v cylc 2> /dev/null)

PGV_VERSION := 1.4rc1
PGV_DISTURL := https://pypi.python.org/packages/25/b1/e44c51b47054ad88aadbe9edcf344bf9b3c61d2d6d15719180ee4d130bcd/pygraphviz-1.4rc1.tar.gz#md5=2f950fb2a61a2dc85efc89543523ec07
PGV_INSTALLDIR := ${HOME}/opt/pygraphviz/${PGV_VERSION}

GV_VERSION := 2.38.0
GV_INSTALLDIR := ${HOME}/opt/graphviz/${GV_VERSION}

define JOBINITENV
# Test 1
# Test 2
endef
export JOBINITENV

################
# check software
################

check-cylc:
ifdef CYLC_CMD
	cylc check-software
else ifneq ("$(wildcard ${CYLC_INSTALLDIR}/bin/cylc)","")
	${CYLC_INSTALLDIR}/bin/cylc check-software
else ifneq ("$(wildcard ${CYLCTMPDIR}/cylc-${CYLC_VERSION}/bin/cylc)","")
	${CYLCTMPDIR}/cylc-${CYLC_VERSION}/bin/cylc check-software
else
	echo "No Cylc software is found."
endif

####################
# Configure software
####################

config-cylc:
ifdef CYLC_CMD
	mkdir -p ${HOME}/.cylc
	cylc get-site-config > ${HOME}/.cylc/global.rc
	echo "" > ${HOME}/.cylc/user.rc
	echo "$$JOBINITENV" > ${HOME}/.cylc/job-init-env.sh
else
	@echo ""
	@echo "*********************************************"
	@echo "  cylc command is not working properly."
	@echo "  Please check PATH and/or Cylc installation."
	@echo "*********************************************"
endif

##################
# Install software
##################

install-graphviz:
	cd ${CYLCTMPDIR}/graphviz-${GV_VERSION}; ./configure --prefix=${GV_INSTALLDIR}
	cd ${CYLCTMPDIR}/graphviz-${GV_VERSION}; make install

install-pygraphviz:
	cd ${CYLCTMPDIR}/pygraphviz-${PGV_VERSION}; python setup.py install --user --library-path=${GV_INSTALLDIR}/lib --include-path=${GV_INSTALLDIR}/include

install-cylc:
	mkdir -p ${CYLC_INSTALLDIR}
	cp -rf ${CYLCTMPDIR}/cylc-${CYLC_VERSION}/* ${CYLC_INSTALLDIR};
	cd ${CYLC_INSTALLDIR}; export PATH=${CYLC_INSTALLDIR}/bin:${PATH}; make; cylc check-software
	cd ${CYLC_INSTALLDIR}; cd ..; ln -s ${CYLC_VERSION} std 
	@echo ""
	@echo "********************************************************************"
	@echo "  Add ${CYLC_INSTALLDIR}/bin to PATH env. variable."
	@echo "********************************************************************"

###################
# Download software	
###################
 
download-graphviz: create_tmpdir
	cd ${CYLCTMPDIR}; wget "http://graphviz.org/pub/graphviz/stable/SOURCES/graphviz-${GV_VERSION}.tar.gz"
	cd ${CYLCTMPDIR}; gunzip ./graphviz-${GV_VERSION}.tar.gz
	cd ${CYLCTMPDIR}; tar -xvf ./graphviz-${GV_VERSION}.tar
	cd ${CYLCTMPDIR}; rm -f ./graphviz-${GV_VERSION}.tar

download-pygraphviz: create_tmpdir
	cd ${CYLCTMPDIR}; wget "${PGV_DISTURL}"
	cd ${CYLCTMPDIR}; gunzip ./pygraphviz-${PGV_VERSION}.tar.gz
	cd ${CYLCTMPDIR}; tar -xvf ./pygraphviz-${PGV_VERSION}.tar
	cd ${CYLCTMPDIR}; rm -f ./pygraphviz-${PGV_VERSION}.tar

download-cylc: create_tmpdir
	cd ${CYLCTMPDIR}; wget "https://github.com/cylc/cylc/archive/${CYLC_VERSION}.tar.gz"
	cd ${CYLCTMPDIR}; mv ${CYLC_VERSION} ${CYLC_VERSION}.tar.gz
	cd ${CYLCTMPDIR}; gunzip ./${CYLC_VERSION}.tar.gz
	cd ${CYLCTMPDIR}; tar -xvf ./${CYLC_VERSION}.tar
	cd ${CYLCTMPDIR}; rm -f ./${CYLC_VERSION}.tar

###############
# Miscellaneous
###############

create_tmpdir:
	mkdir -p ${CYLCTMPDIR}

clean_tmpdir:
	rm -rf ${CYLCTMPDIR}/*
