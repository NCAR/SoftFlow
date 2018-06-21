
explot:
	tigereye \
        WACCM_imp_sol_scaler.slope.labelled.csv \
		--data-format "csv, delimiter=';'" \
		-v "etime:d0.compress(etime[:,2]=='LABEL', etime[:,3].astype(float))" \
		-v "label:d0.compress(label[:,2]=='LABEL', label[:,4].astype(float))" \
		-v "hwc:d0[:,2].unique(hwc).compress([v.endswith('_per_ins') for v in hwc], hwc)" \
		-v "inc:d0.compress(inc[:, 2]=='RESOURCE_STALLS_per_ins', inc[:, 4].astype(float))" \
		-d etime \
		-d label \
		-d inc \
		-p "plot, etime, inc"
		#-x "d0.compress([x[:,2]=='LABEL'], [x[:,3]])" \
		#-v "etime:d0.compress(x[:,2]=='LABEL', x[:,3].astype(float))" \
		#--noplot


load:
	tigereye \
		WACCM_imp_sol_scaler.slope.labelled.csv \
		WACCM_imp_sol_vector.slope.labelled.csv \
		--data-format "csv, delimiter=';'" \
		-v "scalar_etime:d0.compress(scalar_etime[:, 2]=='LABEL', scalar_etime[:, 3].astype(float))" \
		-v "scalar_label:d0.compress(scalar_label[:, 2]=='LABEL', scalar_label[:, 4].astype(float))" \
		-v "vector_etime:d1.compress(vector_etime[:, 2]=='LABEL', vector_etime[:, 3].astype(float))" \
		-v "vector_label:d1.compress(vector_label[:, 2]=='LABEL', vector_label[:, 4].astype(float))" \
		-y "lim=[-2, 2]" \
		-l \
		-t "'WACCM Implicit solver labels for machine learning'" \
		-p "plot, scalar_etime, scalar_label, label='scalar'" \
		-p "plot, scalar_etime, vector_label, label='vector'"
		#--noplot
		#-d x \
		#-d y \

