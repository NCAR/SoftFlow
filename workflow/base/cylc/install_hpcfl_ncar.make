# This makefile is to help installing Cylc on HPC Future Lab cluster of NCAR.

TMPDIR := /lustre/scratch/youngsun/cylcinstall

CYLC_VERSION := 6.11.2
CYLC_INSTALLDIR := ${HOME}/opt/cylc/${CYLC_VERSION}

PGV_VERSION := 1.4rc1
PGV_DISTURL := https://pypi.python.org/packages/25/b1/e44c51b47054ad88aadbe9edcf344bf9b3c61d2d6d15719180ee4d130bcd/pygraphviz-1.4rc1.tar.gz#md5=2f950fb2a61a2dc85efc89543523ec07
PGV_INSTALLDIR := ${HOME}/opt/pygraphviz/${PGV_VERSION}

GV_VERSION := 2.38.0
GV_INSTALLDIR := ${HOME}/opt/graphviz/${GV_VERSION}

check-software:
ifneq ("$(wildcard ${CYLC_INSTALLDIR}/bin/cylc)","")
	${CYLC_INSTALLDIR}/bin/cylc check-software
else ifneq ("$(wildcard ${TMPDIR}/cylc-${CYLC_VERSION}/bin/cylc)","")
	${TMPDIR}/cylc-${CYLC_VERSION}/bin/cylc check-software
else
	echo "No Cylc software is found."
	exit -1
endif

# Install software

install-graphviz:
	cd ${TMPDIR}/graphviz-${GV_VERSION}; ./configure --prefix=${GV_INSTALLDIR}
	cd ${TMPDIR}/graphviz-${GV_VERSION}; make install

install-pygraphviz:
	cd ${TMPDIR}/pygraphviz-${PGV_VERSION}; python setup.py install --user --library-path=${GV_INSTALLDIR}/lib --include-path=${GV_INSTALLDIR}/include

install-cylc:
	mkdir -p ${CYLC_INSTALLDIR}
	cp -rf ${TMPDIR}/cylc-${CYLC_VERSION}/* ${CYLC_INSTALLDIR};
	cd ${CYLC_INSTALLDIR}; export PATH=${CYLC_INSTALLDIR}/bin:${PATH}; make; cylc check-software
	cd ${CYLC_INSTALLDIR}; cd ..; ln -s ${CYLC_VERSION} std 
	@echo ""
	@echo "********************************************************************"
	@echo "  Add ${CYLC_INSTALLDIR}/bin to PATH env. variable."
	@echo "********************************************************************"

# Download software	
 
download-graphviz: create_tmpdir
	cd ${TMPDIR}; wget "http://graphviz.org/pub/graphviz/stable/SOURCES/graphviz-${GV_VERSION}.tar.gz"
	cd ${TMPDIR}; gunzip ./graphviz-${GV_VERSION}.tar.gz
	cd ${TMPDIR}; tar -xvf ./graphviz-${GV_VERSION}.tar
	cd ${TMPDIR}; rm -f ./graphviz-${GV_VERSION}.tar

download-pygraphviz: create_tmpdir
	cd ${TMPDIR}; wget "${PGV_DISTURL}"
	cd ${TMPDIR}; gunzip ./pygraphviz-${PGV_VERSION}.tar.gz
	cd ${TMPDIR}; tar -xvf ./pygraphviz-${PGV_VERSION}.tar
	cd ${TMPDIR}; rm -f ./pygraphviz-${PGV_VERSION}.tar

download-cylc: create_tmpdir
	cd ${TMPDIR}; wget "https://github.com/cylc/cylc/archive/${CYLC_VERSION}.tar.gz"
	cd ${TMPDIR}; gunzip ./${CYLC_VERSION}.tar.gz
	cd ${TMPDIR}; tar -xvf ./${CYLC_VERSION}.tar
	cd ${TMPDIR}; rm -f ./${CYLC_VERSION}.tar

create_tmpdir:
	mkdir -p ${TMPDIR}

clean_tmpdir:
	rm -rf ${TMPDIR}/*
