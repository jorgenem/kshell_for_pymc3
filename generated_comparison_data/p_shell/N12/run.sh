#!/bin/sh 
# export OMP_STACKSIZE=1g
export GFORTRAN_UNBUFFERED_PRECONNECTED=y
# ulimit -s unlimited

# ---------- N12 --------------
cat > N12.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "N12_p.ptn"
  fn_save_wave = "N12_j2p.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 201
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 2
  n_eigen = 1
  n_restart_vec = 1
&end
EOF
nice ./../kshell N12.input > log_N12_j2p.txt 2>&1 

cat > N12.input <<EOF
&input
  beta_cm = 0.d0
  eff_charge = 1.5, 0.5, 
  fn_int = "interaction.snt"
  fn_ptn = "N12_p.ptn"
  fn_save_wave = "N12_j4p.wav"
  gl = 1.0, 0.0, 
  gs = 5.0271, -3.4435, 
  hw_type = 1
  is_double_j = .true.
  max_lanc_vec = 201
  maxiter = 300
  mode_lv_hdd = 1
  mtot = 4
  n_eigen = 1
  n_restart_vec = 1
&end
EOF
nice ./../kshell N12.input > log_N12_j4p.txt 2>&1 

nice ../collect_logs.py log_*N12* > summary_N12.txt
rm -f tmp_snapshot_N12* tmp_lv_N12* N12.input 
rm -f *.wav 
