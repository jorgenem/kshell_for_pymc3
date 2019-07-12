#!/bin/sh 
# export OMP_STACKSIZE=1g
export GFORTRAN_UNBUFFERED_PRECONNECTED=y
# ulimit -s unlimited

# ---------- Be10 --------------
cat > Be10.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "Be10_p.ptn"
  fn_save_wave = "Be10_j0p.wav"
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
nice ./../kshell Be10.input > log_Be10_j0p.txt 2>&1 

cat > Be10.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "Be10_p.ptn"
  fn_save_wave = "Be10_j4p.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 203
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 4
  n_eigen = 2
  n_restart_vec = 3
&end
EOF
nice ./../kshell Be10.input > log_Be10_j4p.txt 2>&1 

nice ../collect_logs.py log_*Be10* > summary_Be10.txt
rm -f tmp_snapshot_Be10* tmp_lv_Be10* Be10.input 
rm -f *.wav 
