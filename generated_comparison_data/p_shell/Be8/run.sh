#!/bin/sh 
# export OMP_STACKSIZE=1g
export GFORTRAN_UNBUFFERED_PRECONNECTED=y
# ulimit -s unlimited

# ---------- Be8 --------------
cat > Be8.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "Be8_p.ptn"
  fn_save_wave = "Be8_j0p.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 204
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 0
  n_eigen = 1
  n_restart_vec = 4
&end
EOF
nice ./../kshell Be8.input > log_Be8_j0p.txt 2>&1 

cat > Be8.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "Be8_p.ptn"
  fn_save_wave = "Be8_j2p.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 204
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 2
  n_eigen = 2
  n_restart_vec = 4
&end
EOF
nice ./../kshell Be8.input > log_Be8_j2p.txt 2>&1 

cat > Be8.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "Be8_p.ptn"
  fn_save_wave = "Be8_j8p.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 204
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 8
  n_eigen = 1
  n_restart_vec = 4
&end
EOF
nice ./../kshell Be8.input > log_Be8_j8p.txt 2>&1 

cat > Be8.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "Be8_p.ptn"
  fn_save_wave = "Be8_j4p.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 204
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 4
  n_eigen = 3
  n_restart_vec = 4
&end
EOF
nice ./../kshell Be8.input > log_Be8_j4p.txt 2>&1 

nice ../collect_logs.py log_*Be8* > summary_Be8.txt
rm -f tmp_snapshot_Be8* tmp_lv_Be8* Be8.input 
rm -f *.wav 
