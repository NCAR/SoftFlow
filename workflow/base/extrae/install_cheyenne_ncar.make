# This makefile is to help installing Extrae on Cori of NERSC

###########
# Variables
###########


INSTALLDIR := /glade/p/tdd/asap/contrib

TMPDIR := /glade/scratch/${USER}
EXTRAETMPDIR := ${TMPDIR}/extraeinstall

# Folding
# https://ftp.tools.bsc.es/folding/folding-1.3.1-src.tar.bz2
FOLDING_VERSION := 1.3.1
FOLDING_INSTALLDIR := ${INSTALLDIR}/folding/${FOLDING_VERSION}

# Extrae
# https://ftp.tools.bsc.es/extrae/extrae-3.4.3-src.tar.bz2
EXTRAE_VERSION := 3.4.3
EXTRAE_INSTALLDIR := ${INSTALLDIR}/extrae/${EXTRAE_VERSION}

# libunwind
# http://download.savannah.gnu.org/releases/libunwind/libunwind-1.2.tar.gz
UNWIND_VERSION := 1.2
UNWIND_INSTALLDIR := ${INSTALLDIR}/libunwind/${UNWIND_VERSION}

# bin-utils
# http://ftp.gnu.org/gnu/binutils/binutils-2.28.tar.gz
BUTILS_VERSION := 2.28
BUTILS_INSTALLDIR := ${INSTALLDIR}/binutils/${BUTILS_VERSION}

# libbfd
BFD_VERSION := 2.28
BFD_INSTALLDIR := ${INSTALLDIR}/binutils/${BUTILS_VERSION}

# libiberty
LIBERTY_VERSION := 2.28
LIBERTY_INSTALLDIR := ${INSTALLDIR}/binutils/${BUTILS_VERSION}

# libxml2
## ftp://xmlsoft.org/libxml2/libxml2-2.9.4.tar.gz
#XML2_VERSION := 2.9.4
#XML2_INSTALLDIR := ${HOME}/opt/xml2/${XML2_VERSION}

# zlib
## http://www.zlib.net/zlib-1.2.11.tar.gz
#ZLIB_VERSION := 1.2.11
#ZLIB_INSTALLDIR := ${HOME}/opt/zlib/${ZLIB_VERSION}

# libpapi
PAPI_VERSION := 5.5.1
PAPI_INSTALLDIR := ${INSTALLDIR}/papi_2017/${PAPI_VERSION}

##################
# Check software
##################

check-papi:

##################
# Install software
##################

install-papi:
	# NOT WORKING YET
	cd ${EXTRAETMPDIR}/papi-${PAPI_VERSION}/src; ./configure --prefix=${PAPI_INSTALLDIR} CC=icc CPP=cpp F77=ifort
	cd ${EXTRAETMPDIR}/papi-${PAPI_VERSION}/src; make install

#install-zlib:
#	cd ${EXTRAETMPDIR}/zlib-${ZLIB_VERSION}; ./configure --prefix=${ZLIB_INSTALLDIR}
#	cd ${EXTRAETMPDIR}/zlib-${ZLIB_VERSION}; make install
#
#install-xml2:
#	cd ${EXTRAETMPDIR}/libxml2-${XML2_VERSION}; ./configure --without-python --prefix=${XML2_INSTALLDIR} \
#		--with-zlib=${ZLIB_INSTALLDIR} --without-lzma
#	cd ${EXTRAETMPDIR}/libxml2-${XML2_VERSION}; make install

#install-binutils:
#	cd ${EXTRAETMPDIR}/binutils-${BUTILS_VERSION}; ./configure --prefix=${BUTILS_INSTALLDIR}
#	cd ${EXTRAETMPDIR}/binutils-${BUTILS_VERSION}; make
#
#install-liberty:
#	cd ${EXTRAETMPDIR}/binutils-${BUTILS_VERSION}/libiberty; ./configure --prefix=${LIBERTY_INSTALLDIR} \
#		CFLAGS="-fPIC"  CXXFLAGS="-fPIC"  LFLAGS="-fPIC" --enable-install-libiberty
#	cd ${EXTRAETMPDIR}/binutils-${BUTILS_VERSION}/libiberty; make install
#
#install-libbfd:
#	cd ${EXTRAETMPDIR}/binutils-${BUTILS_VERSION}/bfd; ./configure --prefix=${BFD_INSTALLDIR} --enable-shared
#	cd ${EXTRAETMPDIR}/binutils-${BUTILS_VERSION}/bfd; make install

install-unwind:
	cd ${EXTRAETMPDIR}/libunwind-${UNWIND_VERSION}; ./configure --prefix=${UNWIND_INSTALLDIR} \
		CC=gcc CXX=g++ FC=gfortran
	cd ${EXTRAETMPDIR}/libunwind-${UNWIND_VERSION}; make clean; make -j 8 install

install-extrae:
	cd ${EXTRAETMPDIR}/extrae-${EXTRAE_VERSION}; ./configure --prefix=${EXTRAE_INSTALLDIR} --enable-sampling \
		CC=gcc CXX=g++ FC=gfortran \
		--with-mpi=/opt/sgi/mpt/mpt-2.15 --with-unwind=${UNWIND_INSTALLDIR} \
		--with-libz=/usr --with-binutils=/usr --with-xml-prefix=/usr \
		--with-papi=/glade/u/apps/ch/opt/papi/5.5.1/intel/16.0.3 \
		--without-dyninst
	cd ${EXTRAETMPDIR}/extrae-${EXTRAE_VERSION}; make clean; make -j 8 install

		#--with-mpi=/opt/sgi/mpt/mpt-2.15 --with-unwind=${UNWIND_INSTALLDIR} \

install-folding:
	cd ${EXTRAETMPDIR}/folding-${FOLDING_VERSION}-intelx86-64; \
		mkdir -p ${FOLDING_INSTALLDIR}; cp -rf * ${FOLDING_INSTALLDIR}

###################
# Download software	
###################
 
download-papi: create_tmpdir
	cd ${EXTRAETMPDIR}; wget "http://icl.utk.edu/projects/papi/downloads/papi-${PAPI_VERSION}.tar.gz"
	cd ${EXTRAETMPDIR}; gunzip ./papi-${PAPI_VERSION}.tar.gz
	cd ${EXTRAETMPDIR}; tar -xvf ./papi-${PAPI_VERSION}.tar
	cd ${EXTRAETMPDIR}; rm -f ./papi-${PAPI_VERSION}.tar

#download-zlib: create_tmpdir
#	cd ${EXTRAETMPDIR}; wget "http://www.zlib.net/zlib-${ZLIB_VERSION}.tar.gz"
#	cd ${EXTRAETMPDIR}; gunzip ./zlib-${ZLIB_VERSION}.tar.gz
#	cd ${EXTRAETMPDIR}; tar -xvf ./zlib-${ZLIB_VERSION}.tar
#	cd ${EXTRAETMPDIR}; rm -f ./zlib-${ZLIB_VERSION}.tar
#
#download-xml2: create_tmpdir
#	cd ${EXTRAETMPDIR}; wget "ftp://xmlsoft.org/libxml2/libxml2-${XML2_VERSION}.tar.gz"
#	cd ${EXTRAETMPDIR}; gunzip ./libxml2-${XML2_VERSION}.tar.gz
#	cd ${EXTRAETMPDIR}; tar -xvf ./libxml2-${XML2_VERSION}.tar
#	cd ${EXTRAETMPDIR}; rm -f ./libxml2-${XML2_VERSION}.tar

#download-liberty: download-binutils 
#download-libbfd: download-binutils
#
#download-binutils: create_tmpdir
#	cd ${EXTRAETMPDIR}; wget "http://ftp.gnu.org/gnu/binutils/binutils-${BUTILS_VERSION}.tar.gz"
#	cd ${EXTRAETMPDIR}; gunzip ./binutils-${BUTILS_VERSION}.tar.gz
#	cd ${EXTRAETMPDIR}; tar -xvf ./binutils-${BUTILS_VERSION}.tar
#	cd ${EXTRAETMPDIR}; rm -f ./binutils-${BUTILS_VERSION}.tar

download-unwind: create_tmpdir
	cd ${EXTRAETMPDIR}; wget "http://download.savannah.gnu.org/releases/libunwind/libunwind-${UNWIND_VERSION}.tar.gz"
	cd ${EXTRAETMPDIR}; gunzip ./libunwind-${UNWIND_VERSION}.tar.gz
	cd ${EXTRAETMPDIR}; tar -xvf ./libunwind-${UNWIND_VERSION}.tar
	cd ${EXTRAETMPDIR}; rm -f ./libunwind-${UNWIND_VERSION}.tar

download-extrae: create_tmpdir
	cd ${EXTRAETMPDIR}; wget "https://ftp.tools.bsc.es/extrae/extrae-${EXTRAE_VERSION}-src.tar.bz2"
	cd ${EXTRAETMPDIR}; bzip2 -d ./extrae-${EXTRAE_VERSION}-src.tar.bz2
	cd ${EXTRAETMPDIR}; tar -xvf ./extrae-${EXTRAE_VERSION}-src.tar
	cd ${EXTRAETMPDIR}; rm -f ./extrae-${EXTRAE_VERSION}-src.tar

download-folding: create_tmpdir
	cd ${EXTRAETMPDIR}; wget "https://ftp.tools.bsc.es/folding/folding-${FOLDING_VERSION}-linux_x86_64.tar.bz2"
	cd ${EXTRAETMPDIR}; bzip2 -d ./folding-${FOLDING_VERSION}-linux_x86_64.tar.bz2
	cd ${EXTRAETMPDIR}; tar -xvf ./folding-${FOLDING_VERSION}-linux_x86_64.tar
	cd ${EXTRAETMPDIR}; rm -f ./folding-${FOLDING_VERSION}-linux_x86_64.tar

###############
# Miscellaneous
###############

create_tmpdir:
	mkdir -p ${EXTRAETMPDIR}

clean_tmpdir:
	rm -rf ${EXTRAETMPDIR}/*
