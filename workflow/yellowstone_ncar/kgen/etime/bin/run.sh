#!/bin/bash


PLOT=/glade/u/home/youngsun/repos/github/SoftFlow/lib/python/plot_etime.py
#APPINI=/glade/u/home/youngsun/trepo/temp/cylcworkspace/_yellowstone_ncar_port_kgen/LW_RRTMGP/output/model.ini
APPINI=/glade/u/home/youngsun/trepo/temp/cylcworkspace/_yellowstone_ncar_port_kgen/SW_RRTMGP/output/model.ini
#KERNELOUTPUT=/glade/u/home/youngsun/trepo/temp/cylcworkspace/_yellowstone_ncar_port_kgen/LW_RRTMGP/output/kernel/run.log
KERNELOUTPUT=/glade/u/home/youngsun/trepo/temp/cylcworkspace/_yellowstone_ncar_port_kgen/SW_RRTMGP/output/kernel/run.log

python ${PLOT} ${APPINI} ${KERNELOUTPUT}
evince etime_report.pdf
