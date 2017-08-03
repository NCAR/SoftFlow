#!/bin/bash

RRTMG_MODEL=/glade/u/home/youngsun/trepo/temp/cylcworkspace/_yellowstone_ncar_kgen_cesm_rrtmg/output/model.ini
RRTMGKERNEL_RUN0=/glade/u/home/youngsun/trepo/temp/cylcworkspace/_yellowstone_ncar_kgen_cesm_rrtmg/output/kernel/run_ys_1_0M.txt
#RRTMGKERNEL_RUN1=/glade/u/home/youngsun/trepo/temp/cylcworkspace/_yellowstone_ncar_kgen_cesm_mg2/output/kernel/run_ys_30_0M.txt
#RRTMGKERNEL_RUN2=/glade/u/home/youngsun/trepo/temp/cylcworkspace/_yellowstone_ncar_kgen_cesm_mg2/output/kernel/run_ys_30_20M.txt
#RRTMGKERNEL_RUN3=/glade/u/home/youngsun/trepo/temp/cylcworkspace/_yellowstone_ncar_kgen_cesm_mg2/output/kernel/run_ys_30_02M.txt

#python plot_etime.py ${RRTMG_MODEL} ${RRTMGKERNEL_RUN0} ${RRTMGKERNEL_RUN1} ${RRTMGKERNEL_RUN2} ${RRTMGKERNEL_RUN3} -o etime_rrtmg_report.pdf --maxval 0.02
#python plot_etime.py ${RRTMG_MODEL} ${RRTMGKERNEL_RUN0}  -o etime_rrtmg_report.pdf --minval 0.003 --maxval 0.005
python plot_etime.py ${RRTMG_MODEL} ${RRTMGKERNEL_RUN0}  -o etime_rrtmg_report.pdf

evince etime_rrtmg_report.pdf 
