#!/bin/bash

MG2PATH=/glade/p/tdd/asap/kgen_data/cesm_mg2

MG2_MODEL=${MG2PATH}/model.ini
MG2KERNEL_RUN0=${MG2PATH}/run_ys_1_0M.txt
MG2KERNEL_RUN1=${MG2PATH}/run_ys_30_0M.txt
MG2KERNEL_RUN2=${MG2PATH}/run_ys_30_20M.txt

python plot_etime.py ${MG2_MODEL} ${MG2KERNEL_RUN0} ${MG2KERNEL_RUN1} ${MG2KERNEL_RUN2} -o etime_mg2.pdf --maxval 0.003

evince etime_mg2.pdf 

