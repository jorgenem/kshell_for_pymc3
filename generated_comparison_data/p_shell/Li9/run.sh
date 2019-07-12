#!/bin/sh 
# export OMP_STACKSIZE=1g
export GFORTRAN_UNBUFFERED_PRECONNECTED=y
# ulimit -s unlimited

# ---------- Li9 --------------
cat > Li9.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "Li9_n.ptn"
  fn_save_wave = "Li9_j3n.wav"
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
nice ./../kshell Li9.input > log_Li9_j3n.txt 2>&1 

nice ../collect_logs.py log_*Li9* > summary_Li9.txt
rm -f tmp_snapshot_Li9* tmp_lv_Li9* Li9.input 
rm -f *.wav 
