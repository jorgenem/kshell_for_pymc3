#!/bin/sh 
# export OMP_STACKSIZE=1g
export GFORTRAN_UNBUFFERED_PRECONNECTED=y
# ulimit -s unlimited

# ---------- C11 --------------
cat > C11.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "C11_n.ptn"
  fn_save_wave = "C11_j1n.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 203
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 1
  n_eigen = 1
  n_restart_vec = 3
&end
EOF
nice ./../kshell C11.input > log_C11_j1n.txt 2>&1 

cat > C11.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "C11_n.ptn"
  fn_save_wave = "C11_j5n.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 203
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 5
  n_eigen = 1
  n_restart_vec = 3
&end
EOF
nice ./../kshell C11.input > log_C11_j5n.txt 2>&1 

cat > C11.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "C11_n.ptn"
  fn_save_wave = "C11_j3n.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 203
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 3
  n_eigen = 2
  n_restart_vec = 3
&end
EOF
nice ./../kshell C11.input > log_C11_j3n.txt 2>&1 

nice ../collect_logs.py log_*C11* > summary_C11.txt
rm -f tmp_snapshot_C11* tmp_lv_C11* C11.input 
rm -f *.wav 
