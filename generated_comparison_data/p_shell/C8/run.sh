#!/bin/sh 
# export OMP_STACKSIZE=1g
export GFORTRAN_UNBUFFERED_PRECONNECTED=y
# ulimit -s unlimited

# ---------- C8 --------------
cat > C8.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "C8_p.ptn"
  fn_save_wave = "C8_j0p.wav"
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
nice ./../kshell C8.input > log_C8_j0p.txt 2>&1 

nice ../collect_logs.py log_*C8* > summary_C8.txt
rm -f tmp_snapshot_C8* tmp_lv_C8* C8.input 
rm -f *.wav 
