#!/bin/sh 
# export OMP_STACKSIZE=1g
export GFORTRAN_UNBUFFERED_PRECONNECTED=y
# ulimit -s unlimited

# ---------- C13 --------------
cat > C13.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "C13_n.ptn"
  fn_save_wave = "C13_j1n.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 201
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 1
  n_eigen = 1
  n_restart_vec = 1
&end
EOF
nice ./../kshell C13.input > log_C13_j1n.txt 2>&1 

nice ../collect_logs.py log_*C13* > summary_C13.txt
rm -f tmp_snapshot_C13* tmp_lv_C13* C13.input 
rm -f *.wav 
