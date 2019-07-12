#!/bin/sh 
# export OMP_STACKSIZE=1g
export GFORTRAN_UNBUFFERED_PRECONNECTED=y
# ulimit -s unlimited

# ---------- N14 --------------
cat > N14.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "N14_p.ptn"
  fn_save_wave = "N14_j0p.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 203
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 0
  n_eigen = 1
  n_restart_vec = 3
&end
EOF
nice ./../kshell N14.input > log_N14_j0p.txt 2>&1 

cat > N14.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "N14_p.ptn"
  fn_save_wave = "N14_j2p.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 203
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 2
  n_eigen = 2
  n_restart_vec = 3
&end
EOF
nice ./../kshell N14.input > log_N14_j2p.txt 2>&1 

nice ../collect_logs.py log_*N14* > summary_N14.txt
rm -f tmp_snapshot_N14* tmp_lv_N14* N14.input 
rm -f *.wav 
