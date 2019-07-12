# kshell_for_pymc3
A wrapper code to interface shell model calculations in KSHELL with the monte carlo inference tool PyMC3, facilitating bayesian optimization of shell model interaction parameters

To be used together with the code found in https://github.com/jorgenem/kshell_public/

It requires the following python libraries: `pymc3, numpy, scipy, collections2`
There is some mixing between python2.7 and python3, unfortunately. Some of the kshell utility scripts require python2, while pymc3 only runs on python3.

Some words on the module structure:
* The class ChiSquare is a Theano Op, which is the data structure required to make it talk to PyMC3. Here is a nice blog post explaining how this works, which is actually inspired by the code in this repo: http://mattpitkin.github.io/samplers-demo/pages/pymc3-blackbox-likelihood/
* The class ChiSquareGrad is another Theano Op, and takes care of the gradient of the ChiSquare. To evaluate the gradient of the chisquare, which by the chain rule requires the gradient of the Hamiltonian, I exploit the Feynman-Hellman theorem to crack open the dependence of the gradient on the individual two-body matrix element expectation values. The paper by Brown et al on the USDa interaction fit has some nice math on this.
* The class ShellModelEnsemble() is responsible for setting up and executing shell model calculations for an "ensemble", that is a set, of nuclei. This is the call that the ChiSquare and ChiSquareGrad makes at every new parameter point to get information for the chisquare.
* The ShellModelEnsemble() again calls another class for each nucleus in the ensemble, called ShellModelCalculation. This class is not in the present repo, but instead included with my version of KSHELL located in https://github.com/jorgenem/kshell_public/ (in the folder `bin/`).
* It is often necessary to evaluate the same parameter point several times, e.g. when both the chisquare and the chisquaregrad are called separately. To avoid double labour, each calculation is stored in a folder called `steps`, in a folder that is named by a long number which is unique to each set of parameter values. The code checks if the right number is present before calling the ensemble of calculations.