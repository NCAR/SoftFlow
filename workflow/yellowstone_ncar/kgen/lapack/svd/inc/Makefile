
FC := ifort
FCFLAGS :=
LAPACKLIBS := /glade/u/home/youngsun/repos/github/lapack-release/liblapack.a /glade/u/home/youngsun/repos/github/lapack-release/librefblas.a /glade/u/home/youngsun/repos/github/lapack-release/libtmglib.a
#LAPACKSRC := /glade/u/home/youngsun/repos/github/lapack-release/SRC
#LAPACKSRC := /glade/u/home/youngsun/trepo/temp/lapack3e/LAPACK3E/SRC

run:
	./svdtest

build: main.o driver.o
	${FC} ${FCFLAGS} -o svdtest main.o driver.o ${LAPACKLIBS}

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
