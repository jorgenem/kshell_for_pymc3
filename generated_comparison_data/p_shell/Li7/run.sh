#!/bin/sh 
# export OMP_STACKSIZE=1g
export GFORTRAN_UNBUFFERED_PRECONNECTED=y
# ulimit -s unlimited

# ---------- Li7 --------------
cat > Li7.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "Li7_n.ptn"
  fn_save_wave = "Li7_j7n.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 204
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 7
  n_eigen = 2
  n_restart_vec = 4
&end
EOF
nice ./../kshell Li7.input > log_Li7_j7n.txt 2>&1 

cat > Li7.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "Li7_n.ptn"
  fn_save_wave = "Li7_j1n.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 204
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 1
  n_eigen = 1
  n_restart_vec = 4
&end
EOF
nice ./../kshell Li7.input > log_Li7_j1n.txt 2>&1 

cat > Li7.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "Li7_n.ptn"
  fn_save_wave = "Li7_j5n.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 204
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 5
  n_eigen = 2
  n_restart_vec = 4
&end
EOF
nice ./../kshell Li7.input > log_Li7_j5n.txt 2>&1 

cat > Li7.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "Li7_n.ptn"
  fn_save_wave = "Li7_j3n.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 204
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 3
  n_eigen = 3
  n_restart_vec = 4
&end
EOF
nice ./../kshell Li7.input > log_Li7_j3n.txt 2>&1 

nice ../collect_logs.py log_*Li7* > summary_Li7.txt
rm -f tmp_snapshot_Li7* tmp_lv_Li7* Li7.input 
rm -f *.wav 
