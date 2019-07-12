#!/bin/sh 
# export OMP_STACKSIZE=1g
export GFORTRAN_UNBUFFERED_PRECONNECTED=y
# ulimit -s unlimited

# ---------- He5 --------------
cat > He5.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "He5_n.ptn"
  fn_save_wave = "He5_j3n.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 201
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 3
  n_eigen = 1
  n_restart_vec = 1
&end
EOF
nice ./../kshell He5.input > log_He5_j3n.txt 2>&1 

nice ../collect_logs.py log_*He5* > summary_He5.txt
rm -f tmp_snapshot_He5* tmp_lv_He5* He5.input 
rm -f *.wav 
