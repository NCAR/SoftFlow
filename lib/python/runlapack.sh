#!/bin/bash

LAPACK_MODEL=/glade/u/home/youngsun/trepo/temp/cylcworkspace/_yellowstone_ncar_kgen_lapack_svd/output/model.ini
LAPACKKERNEL_RUN0=/glade/u/home/youngsun/trepo/temp/cylcworkspace/_yellowstone_ncar_kgen_lapack_svd/output/kernel/run_ys_1_0M.txt
#LAPACKKERNEL_RUN1=/glade/u/home/youngsun/trepo/temp/cylcworkspace/_yellowstone_ncar_kgen_cesm_mg2/output/kernel/run_ys_30_0M.txt
#LAPACKKERNEL_RUN2=/glade/u/home/youngsun/trepo/temp/cylcworkspace/_yellowstone_ncar_kgen_cesm_mg2/output/kernel/run_ys_30_20M.txt
#LAPACKKERNEL_RUN3=/glade/u/home/youngsun/trepo/temp/cylcworkspace/_yellowstone_ncar_kgen_cesm_mg2/output/kernel/run_ys_30_02M.txt

#python plot_etime.py ${LAPACK_MODEL} ${LAPACKKERNEL_RUN0} ${LAPACKKERNEL_RUN1} ${LAPACKKERNEL_RUN2} ${LAPACKKERNEL_RUN3} -o etime_rrtmg_report.pdf --maxval 0.02
#python plot_etime.py ${LAPACK_MODEL} ${LAPACKKERNEL_RUN0}  -o etime_rrtmg_report.pdf --minval 0.003 --maxval 0.005
python plot_etime.py ${LAPACK_MODEL} ${LAPACKKERNEL_RUN0}  -o etime_lapack_report.pdf -t "Lapack SVD"

evince etime_lapack_report.pdf 
