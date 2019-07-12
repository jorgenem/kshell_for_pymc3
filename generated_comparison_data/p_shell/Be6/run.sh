#!/bin/sh 
# export OMP_STACKSIZE=1g
export GFORTRAN_UNBUFFERED_PRECONNECTED=y
# ulimit -s unlimited

# ---------- Be6 --------------
cat > Be6.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "Be6_p.ptn"
  fn_save_wave = "Be6_j0p.wav"
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
nice ./../kshell Be6.input > log_Be6_j0p.txt 2>&1 

nice ../collect_logs.py log_*Be6* > summary_Be6.txt
rm -f tmp_snapshot_Be6* tmp_lv_Be6* Be6.input 
rm -f *.wav 
