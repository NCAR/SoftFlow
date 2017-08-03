
FC := ifort
FCFLAGS :=
LAPACKLIBS := /glade/u/home/youngsun/repos/github/lapack-release/liblapack.a /glade/u/home/youngsun/repos/github/lapack-release/librefblas.a /glade/u/home/youngsun/repos/github/lapack-release/libtmglib.a
#LAPACKSRC := /glade/u/home/youngsun/repos/github/lapack-release/SRC
#LAPACKSRC := /glade/u/home/youngsun/trepo/temp/lapack3e/LAPACK3E/SRC

#EXTRAE_HOME := /glade/p/tdd/asap/contrib/cheyenne_packages/extrae/3.4.3
EXTRAE_HOME := /glade/p/tdd/asap/contrib/cheyenne_packages/extrae/3.5.1
EXTRAE_CONFIG_FILE=extrae.xml

PAPI_HOME := /glade/p/tdd/asap/contrib/cheyenne_packages/papi_2017/5.5.1
XML_HOME := /glade/apps/opt/libxml2/2.9.0/gnu/4.7.2
UNWIND_HOME := /glade/p/tdd/asap/contrib/cheyenne_packages/libunwind/1.2

PAPILIB := -L${PAPI_HOME}/lib -lpapi
XMLLIB := -L${XML_HOME}/lib -lxml2
UNWINDLIB := -L${XML_HOME}/lib -lunwind
LIBERTYLIB := /usr/lib64/libiberty.a
EXTRAELIB := -L${EXTRAE_HOME}/lib -lseqtrace

ALLLIBS := ${LAPACKLIBS} ${PAPILIB} ${XMLLILB} ${UNWINDLIB} ${LIBERTYLIB} ${EXTRAELIB}

LIBPATHS := ${EXTRAE_HOME}/lib:${XML_HOME}/lib:${XML_HOME}/lib:${PAPI_HOME}/lib

PRERUN := export EXTRAE_HOME=${EXTRAE_HOME}; export EXTRAE_CONFIG_FILE=${EXTRAE_CONFIG_FILE}; export LD_LIBRARY_PATH=${LIBPATHS}:${LD_LIBRARY_PATH}

build: main.o driver.o
	${FC} ${FCFLAGS} -o svdtest main.o driver.o ${ALLLIBS}

run:
	${PRERUN}; ./svdtest

main.o : main.f90 driver.o
	$(FC) -c ${FCFLAGS} $< -o $@

driver.o : driver.f90
	$(FC) -c ${FCFLAGS} $< -o $@

%.o: ${LAPACKSRC}/%.F
	${FC} -c -o $@ $<

%.o: ${LAPACKSRC}/%.f
	${FC} -c -o $@ $<

clean:
	rm -f svdtest *.o *.mod
