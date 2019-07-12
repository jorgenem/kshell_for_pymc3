#!/bin/sh 
# export OMP_STACKSIZE=1g
export GFORTRAN_UNBUFFERED_PRECONNECTED=y
# ulimit -s unlimited

# ---------- Li8 --------------
cat > Li8.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "Li8_p.ptn"
  fn_save_wave = "Li8_j6p.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 204
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 6
  n_eigen = 1
  n_restart_vec = 4
&end
EOF
nice ./../kshell Li8.input > log_Li8_j6p.txt 2>&1 

cat > Li8.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "Li8_p.ptn"
  fn_save_wave = "Li8_j2p.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 204
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 2
  n_eigen = 3
  n_restart_vec = 4
&end
EOF
nice ./../kshell Li8.input > log_Li8_j2p.txt 2>&1 

cat > Li8.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "Li8_p.ptn"
  fn_save_wave = "Li8_j4p.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 204
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 4
  n_eigen = 1
  n_restart_vec = 4
&end
EOF
nice ./../kshell Li8.input > log_Li8_j4p.txt 2>&1 

nice ../collect_logs.py log_*Li8* > summary_Li8.txt
rm -f tmp_snapshot_Li8* tmp_lv_Li8* Li8.input 
rm -f *.wav 
