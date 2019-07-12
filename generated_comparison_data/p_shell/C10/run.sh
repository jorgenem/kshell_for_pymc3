#!/bin/sh 
# export OMP_STACKSIZE=1g
export GFORTRAN_UNBUFFERED_PRECONNECTED=y
# ulimit -s unlimited

# ---------- C10 --------------
cat > C10.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "C10_p.ptn"
  fn_save_wave = "C10_j0p.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 201
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 0
  n_eigen = 1
  n_restart_vec = 1
&end
EOF
nice ./../kshell C10.input > log_C10_j0p.txt 2>&1 

cat > C10.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "C10_p.ptn"
  fn_save_wave = "C10_j4p.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 201
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 4
  n_eigen = 1
  n_restart_vec = 1
&end
EOF
nice ./../kshell C10.input > log_C10_j4p.txt 2>&1 

nice ../collect_logs.py log_*C10* > summary_C10.txt
rm -f tmp_snapshot_C10* tmp_lv_C10* C10.input 
rm -f *.wav 
