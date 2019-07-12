#!/bin/sh 
# export OMP_STACKSIZE=1g
export GFORTRAN_UNBUFFERED_PRECONNECTED=y
# ulimit -s unlimited

# ---------- C12 --------------
cat > C12.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "C12_p.ptn"
  fn_save_wave = "C12_j0p.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 203
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 0
  n_eigen = 2
  n_restart_vec = 3
&end
EOF
nice ./../kshell C12.input > log_C12_j0p.txt 2>&1 

cat > C12.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "C12_p.ptn"
  fn_save_wave = "C12_j4p.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 203
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 4
  n_eigen = 1
  n_restart_vec = 3
&end
EOF
nice ./../kshell C12.input > log_C12_j4p.txt 2>&1 

nice ../collect_logs.py log_*C12* > summary_C12.txt
rm -f tmp_snapshot_C12* tmp_lv_C12* C12.input 
rm -f *.wav 
