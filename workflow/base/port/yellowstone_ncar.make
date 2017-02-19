# Makefile for PORT project

# directories
SRCDIR ?= /glade/u/home/youngsun/apps/port/rrtmgp14_cam5_4_48

build-rrtmg:
	${SRCDIR}/f19c5aqportm-1d.sh -b 

build-rrtmgp:
	${SRCDIR}/f19c5aqrpportm-1d.sh -b 

run-rrtmg:
	bsub < ${SRCDIR}/f19c5aqportm-1d.sh

run-rrtmgp:
	bsub < ${SRCDIR}/f19c5aqrpportm-1d.sh
