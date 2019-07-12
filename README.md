# kshell_for_pymc3
A wrapper code to interface shell model calculations in KSHELL with the monte carlo inference tool PyMC3, facilitating bayesian optimization of shell model interaction parameters

To be used together with the code found in https://github.com/jorgenem/kshell_public/


requires the following python libraries: `pymc3, numpy, scipy, collections2`
There is some mixing between python2.7 and python3, unfortunately. Some of the kshell utility scripts require python2, while pymc3 only runs on python3.
