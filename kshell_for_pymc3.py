# from scipy import optimize, special
import numpy as np
import theano as th
# import matplotlib.pyplot as plt
import sys
import os
import shutil
from collections import OrderedDict

# Import settings from kshell_settings.py:
from kshell_settings import KSHELL_DIR, IS_MPI
# Then import utility scripts from KSHELL_DIR/bin folder:
sys.path.insert(0, os.path.join(KSHELL_DIR, "bin"))
import shellmodelcalculation as smcalc
import shellmodelutilities as smutil
import gen_partition_batchmode as gp


# Set random seed
np.random.seed(506)



""" 
From http://docs.pymc.io/advanced_theano.html

"Good reasons for defining a custom Op might be the following:
...
You want to connect your PyMC3 model to some existing external code."
"""


# == Set global values for kshell run parameters, a bit messy to have it here but should work:
# max_lanc_vec = 200+int(1.5*max_num_levels(nucleusSMC.levels))
# max_lanc_vec = 200+int(10*max_num_levels(nucleusSMC.levels))
max_lanc_vec = 10
# max_lanc_vec = 500
# max_lanc_vec = 1000 # Too large -- gives JJ collapse trouble.
# n_restart_vec = max_lanc_vec - 200
n_restart_vec = 1 # Very low values seems to make it more stable against JJ collapse


# === Utility functions ===
def sum_num_levels(levels):
    # Assumes all levels have all spins assigned with decimal, e.g. "2.0+2", "3.5+1" etc.
    N = 0
    for level in levels:
        # print level
        N += int(level[4:])
    return N

def max_num_levels(levels):
    maxval = 0
    for level in levels:
        # print level, level[4:]
        if int(level[4:]) > maxval:
            maxval = int(level[4:])
    return maxval



# === Class which sets up and runs an ensemble of shell model calculations, called in each MC step ===

class ShellModelEnsemble:
    """
    Run shell model calculations for an ensemble of nuclei, returning a matrix of their calc_tbme expectation values.
    
    TODO: Will need to implement a mechanism for adding penalty in case not all states are found.
    """

    def __init__(self, core, model_space, spe_template, tbme_template, nucleiList, kshell_dir, mass_scaling=False, scaling_A0=0, scaling_p=0, 
                             is_mpi=False, num_nodes=1, trans_e2m1=False, trans_e1=False, max_lanc_vec=200, maxiter=300, n_restart_vec=10, hw_type=1, 
                             mode_lv_hdd=0, eff_charge=[1.5, 0.5], gl=[1.0, 0.0], gs=[5.0271, -3.4435], beta_cm='0.d0'):
        self.core = core
        self.model_space = model_space
        self.spe_template = spe_template
        self.tbme_template = tbme_template[np.lexsort((tbme_template[:,4],tbme_template[:,3],tbme_template[:,2],tbme_template[:,1],tbme_template[:,0]))]
        self.nucleiList = OrderedDict(sorted(nucleiList.items()))
        self.kshell_dir = kshell_dir

        # Mass scaling parameters to be passed to interaction file. Only used if mass_scaling=True
        self.mass_scaling = mass_scaling
        self.scaling_A0 = scaling_A0
        self.scaling_p = scaling_p

        self.is_mpi = is_mpi
        self.Nspe = len(self.model_space)
        self.Ntbme = len(self.tbme_template[:,0])
        self.Ntot = 0
        for nucleusName, nucleusAttr in nucleiList.items():
            self.Ntot += sum_num_levels(nucleusAttr["levels"])
        # print "Total number of levels Ntot =", self.Ntot
        # Copy binary files to top directory
        self.fname_allstepsdir = "steps"
        # = first make sure steps folder exists
        if not os.path.exists(self.fname_allstepsdir):
            os.makedirs(self.fname_allstepsdir)
        fn_kshell = "kshell_mpi" if is_mpi and not is_mpi=="batch_single" else "kshell"
        fn_transit = "transit_mpi" if is_mpi and not is_mpi=="batch_single" else "transit"
        fn_collectlogs = "collect_logs.py"
        if not (os.path.isfile(fn_kshell) and os.path.isfile(fn_transit) and os.path.isfile(fn_collectlogs)):
            shutil.copy( os.path.join(self.kshell_dir, "bin/"+fn_kshell), self.fname_allstepsdir+"/" )
            # # except IOError:
            #         raise Exception("\n*** WARNING: copying kshell binary to current dir. failed ***")
            try:
                    shutil.copy( os.path.join(self.kshell_dir, "bin/"+fn_transit), self.fname_allstepsdir+"/" )
            except IOError:
                    raise Exception("\n*** WARNING: copying transit binary to current dir. failed ***")
            try:
                    shutil.copy( os.path.join(self.kshell_dir, "bin/"+fn_collectlogs), self.fname_allstepsdir+"/" )
            except IOError:
                    raise Exception("\n*** WARNING: copying collect_logs.py to current dir. failed ***")

        # Make partition files and runscripts once and for all, put them in directory kshell_partition_files / kshell_run_scripts:

        fname_ptndir = "kshell_partition_files"
        if not os.path.exists(fname_ptndir):
            os.makedirs(fname_ptndir)
        fname_runscriptdir = "kshell_run_scripts"
        if not os.path.exists(fname_runscriptdir):
            os.makedirs(fname_runscriptdir)

        # Write interaction using template parameters, required to make partition files
        fname_interaction_template = "interaction_template.snt"
        smutil.write_interaction_file_msdict(os.path.join(fname_ptndir, fname_interaction_template), self.spe_template, self.tbme_template, self.model_space, self.core, comments="Autogenerated by shell_model_calculation class.")

        for nucleusName, nucleusAttr in self.nucleiList.items():
            os.chdir(fname_ptndir)
            nferm = (nucleusAttr["Z"]-self.core["Z"], (nucleusAttr["A"]-self.core["A"])-(nucleusAttr["Z"]-self.core["Z"]))
            allowed_parities = []
            for nparity in [+1, -1]:
                if gp.check_parity(fname_interaction_template, nferm, nparity): # Checking if the current nucleus has any states in given parity before trying to generate partition file.
                    allowed_parities.append(nparity) # If the parity is allowed for current nucleus, add it to list.
                    # print "Generating with parity {:s}".format("+" if nparity > 0 else "-") 
                    fn_ptn = nucleusName+"_{:s}.ptn".format("p" if nparity > 0 else "n")
                    gp.main("interaction_template.snt", fn_ptn, nferm, nparity, nucleusAttr["truncation"])
            os.chdir("../") # Step out from fname_ptndir to top directory



            os.chdir(fname_runscriptdir)

            # Set up run script for current nucleus
            var_dict = {
                "max_lanc_vec"    : max_lanc_vec , 
                "maxiter"             : maxiter , 
                "n_restart_vec" : n_restart_vec , 
                "hw_type"             : hw_type, 
                "mode_lv_hdd"     : mode_lv_hdd, 
                "eff_charge"        : eff_charge, 
                "gl"                        : gl, 
                "gs"                        : gs,
                "beta_cm"             : beta_cm,
            }
    
            # Ask KSHELL to calculate expectation values of TBMEs for each level if switch is on -- which we need for chisquare gradient:
            var_dict["is_calc_tbme"] = ".true."
    
            out = smcalc.batch_script_header(is_mpi, num_nodes, "run.sh")
            # TODO Add paragraphs for each J- or M-projected calculation
            #            Modify it so that it calls binary files from top directory rather than copying to each rundir
    
            out += '# ---------- ' + nucleusName + ' --------------\n'
    
            if len(nucleusAttr["levels"])==1 and nucleusAttr["levels"][0].isdigit(): nucleusAttr["levels"] = ['+'+nucleusAttr["levels"][0], '-'+nucleusAttr["levels"][0]]
            nferm = (nucleusAttr["Z"]-self.core["Z"], (nucleusAttr["A"]-self.core["A"])-(nucleusAttr["Z"]-self.core["Z"]))
            list_jpn = [ smcalc.split_jpn(a, nferm) for a in nucleusAttr["levels"] ]
            # for j,p,n,isp in list_jpn:
            #         if (j+sum(nferm))%2 != 0: print "Removed illegal states J,prty,Num=",j,p,n,isp
            list_jpn = [ a for a in list_jpn if ( (a[0]+sum(nferm))%2==0 and a[1] in allowed_parities) ] # JEM 20170809: Added check for allowed parity.
            list_prty = list( set( jpn[1] for jpn in list_jpn ) )
            fn_base = nucleusName
            fn_input = fn_base + ".input"
            fn_ptn_list = {-1:"../../../kshell_partition_files/"+fn_base+"_n.ptn", 1:"../../../kshell_partition_files/"+fn_base+"_p.ptn"}
    
            fn_save_list = {}
            for mtot,nparity,n_eigen,is_proj in list_jpn:
                # print "hello from loop"
                if is_proj: 
                    jchar = '_j'
                    var_dict[ 'is_double_j' ] = '.true.'
                else: 
                    jchar =    '_m'
                    var_dict[ 'is_double_j' ] = '.false.'
                var_dict[ "fn_ptn" ] = '"' + fn_ptn_list[nparity] + '"'
                fn_save_wave = '"' + fn_base + jchar + str(mtot) \
                                            + smcalc.prty2str(nparity) + '.wav"'
                fn_log = 'log_' + fn_base + jchar + str(mtot) \
                                + smcalc.prty2str(nparity) + '.txt'
                var_dict[ 'fn_save_wave' ] = fn_save_wave
                fn_save_list[ (mtot,nparity) ] = fn_save_wave, var_dict[ 'fn_ptn' ] 
                var_dict[ 'n_eigen' ] = n_eigen
                var_dict[ 'n_restart_vec' ] = max( n_eigen, int(var_dict[ 'n_restart_vec' ]) )
                if int(var_dict[ 'n_restart_vec' ]) > var_dict[ 'max_lanc_vec' ]:
                    var_dict[ "max_lanc_vec" ]    = int(var_dict[ "n_restart_vec" ]) + 100
                var_dict[ 'mtot' ] = mtot
                var_dict['fn_int'] = '"../interaction.snt"'
                 
                # out += 'echo "\nstart running ' + fn_log + ' ..."\n' 
                out += 'cat > ' + fn_input + ' <<EOF\n' \
                     +    '&input\n'
                out += smcalc.print_var_dict( var_dict )
                out += '&end\n' \
                     +    'EOF\n'
                out +=    smcalc.exec_string('../../kshell', fn_input, fn_log, is_mpi)
    
                list_prty = list( set( jpn[1] for jpn in list_jpn ) )
            if len(list_prty)<2: is_e1 = False

            if trans_e2m1 or trans_e1:
                out += "# --------------- transition probabilities --------------\n\n"
                for i1, (m1, np1, ne1, isj1) in enumerate(list_jpn):
                        for i2, (m2, np2, ne2, isj2) in enumerate(list_jpn):
                                if i1 > i2: continue
                                if (isj1 and m1==0) and (isj2 and m2==0): continue
                                is_skip = True
                                if trans_e2m1: 
                                        if abs(m1-m2) <= 4 and np1 == np2: is_skip = False
                                if trans_e1:
                                        if abs(m1-m2) <= 2 and np1 != np2: is_skip = False
                                if is_skip: continue
                                out += output_transit(fn_base, fn_input, fn_save_list, fn_save_list, 
                                                                            (m1, np1, ne1, isj1), (m2, np2, ne2, isj2) )
    
            
            
                # TODO Add option of calculating transitions
    
            
            
                # Finish up run script
            fn_summary = 'summary_' + fn_base + '.txt'
            out += "nice ../../collect_logs.py log_*" + fn_base + "* > " + fn_summary + "\n"
            out += 'rm -f tmp_snapshot_' + fn_base + '* tmp_lv_' + fn_base + '* ' \
                 + fn_input + ' \n'
            out += 'rm -f *.wav \n' # WARNING: This deletes the wavefunctions to save space.
            # out += 'tar czvf logs_'+fn_base+'.tar.gz *.txt *.snt *.ptn *.sh \n' # JEM addition 20170612
            # out += 'echo "Finish computing '+fn_base+'.        See ' + fn_summary + '"\n'
            # out += 'echo \n\n'
    
            with open('run_'+nucleusName+'.sh', 'w') as f:
                f.write(out)
            os.chdir("../") # step out from fname_runscriptdir to top directory


    def run(self, spe_tbme):
        # Add some test in case spe_tbme is a Theano tensor?
        # print type(spe_tbme)
        # print spe_tbme.ndim
        # if type(spe_tbme) == "<class 'theano.tensor.var.TensorVariable'>":
        #     print "Oh hello"
        #     Nspetbme = spe_tbme.ndim
        # else:
        #     Nspetbme = len(spe_tbme)

        # calc_tbme_matrix = np.zeros((self.Ntot,self.Nspe+self.Ntbme))
        calc_dict = {}
        # print "From smensemble.run(): calc_tbme_matrix.shape =", calc_tbme_matrix.shape
        SPE = spe_tbme[0:self.Nspe]

        tbme_template = self.tbme_template
        # print "SPE =", SPE
        # TBME = np.copy(self.tbme_template)
        # print TBME[:,5]
        # print "spe_tbme =", spe_tbme
        # print "spe_tbme.shape =", spe_tbme.shape
        # TBME[:,5] = spe_tbme[self.Nspe:]
        # TBME_th = th.tensor.stack([tbme_template[0:5,:], spe_tbme[self.Nspe:].reshape((self.Ntbme,1))])
        TBME_input1 = th.tensor.dmatrix("TBME_input1")
        TBME_input1.tag.test_value = self.tbme_template[:,0:5]
        # print "TBME_input1.tag.test_value.shape =", TBME_input1.tag.test_value.shape 
        TBME_input2 = th.tensor.dvector("TBME_input2")
        TBME_input2.tag.test_value = np.random.rand(self.Ntbme)
        # print "TBME_input2.tag.test_value.shape =", TBME_input2.tag.test_value.shape 
        TBME_th = th.tensor.concatenate([TBME_input1, TBME_input2.reshape((TBME_input2.shape[0],1))], axis=1)
        TBME_values = th.function([TBME_input1, TBME_input2], TBME_th)
        TBME = TBME_values(tbme_template[:,0:5], spe_tbme[self.Nspe:])
        # Make new directory for each calculation to store everything
        os.chdir(self.fname_allstepsdir) 
        fname_currentstepdir = "{:d}".format(int((np.abs(spe_tbme)*np.linspace(1,len(spe_tbme)+1,len(spe_tbme))).sum()*1e25)) # Each folder is named by the sum of parameter values. 
                                                                                                         # This is to make it identifiable so we don't rerun an
                                                                                                         # ensemble with the same parameters, e.g. for taking 
                                                                                                         # the gradient. It may be a stupid way to do it, suggestions
                                                                                                         # welcome.
        if not os.path.exists(fname_currentstepdir):
            os.makedirs(fname_currentstepdir)
        os.chdir(fname_currentstepdir)

        # Write interaction file:
        # print self.mass_scaling, self.scaling_A0, self.scaling_p
        smutil.write_interaction_file_msdict("interaction.snt", SPE, TBME, self.model_space, self.core, comments="Autogenerated by ShellModelEnsemble class.", mass_scaling=self.mass_scaling, scaling_A0=self.scaling_A0, scaling_p=self.scaling_p)



        i_level = 0
        for nucleusName, nucleusAttr in self.nucleiList.items():
            rundirName = "{:s}".format(nucleusName) # Temporary directory where KSHELL runs for current nucleus, e.g. O18
            outputFilename = "summary_{:s}.txt".format(nucleusName) # The name of the summary file for current nucleus that we want to keep by moving it up
            # outputFilenameFinal =    "summary-{:s}.txt".format(nucleusName) # TODO remove if not needed
            # nucleusSMC = smcalc.shellmodelcalculation(nucleusName,
                # A=nucleusAttr["A"], Z=nucleusAttr["Z"],
                # levels=nucleusAttr["levels"],
                # truncation=nucleusAttr["truncation"],
                # core=self.core, model_space=self.model_space, SPE=SPE,
                # TBME=TBME, kshell_dir=KSHELL_DIR, calc_tbme=True,
                # ensemble_run=True)
            nucleusSMC = smcalc.shellmodelcalculation(nucleusName,
                A=nucleusAttr["A"], Z=nucleusAttr["Z"],
                levels=nucleusAttr["levels"],
                truncation=nucleusAttr["truncation"], core=self.core,
                model_space=self.model_space, SPE=SPE, TBME=TBME,
                kshell_dir=KSHELL_DIR, calc_tbme=True,
                ensemble_run=False)

            # Run calculation and extract spe&tbme expectation values, wrapped in some tests to avoid unnecessary steps:
            if os.path.isfile(os.path.join(rundirName, outputFilename)): # If the rundir exists for current nucleus then we must 
                try:  # It could be that the step was cancelled in the middle of this nucleus. So we try to catch the exception that the results file is not complete
                         # levels = smutil.read_energy_levels(os.path.join(rundirName, outputFilename))
                    calc_tbmes = smutil.read_calc_tbme(os.path.join(rundirName, outputFilename), self.tbme_template)
                    calc_E = smutil.read_energy_levels(os.path.join(rundirName, outputFilename))
                except: # If exception is raised then it means the output file is incomplete and we need to rerun this nucleus.
                    # nucleusSMC.run(is_mpi=self.is_mpi, n_restart_vec=n_restart_vec, max_lanc_vec=max_lanc_vec) 
                    nucleusSMC.run(is_mpi=self.is_mpi) #    n_restart_vec, max_lanc_vec set in initialization for tuning run
                    levels = smutil.read_energy_levels(os.path.join(rundirName, outputFilename))
                    calc_tbmes = smutil.read_calc_tbme(os.path.join(rundirName, outputFilename), self.tbme_template)
                    calc_E = smutil.read_energy_levels(os.path.join(rundirName, outputFilename))
                    shutil.copyfile(os.path.join(rundirName, outputFilename), outputFilename) # Copy results file to current step directory and remove current rundir
                    shutil.rmtree(rundirName)
            elif os.path.isfile(outputFilename): # The current nucleus has been completed, and the summary has been copied to outputFilenameFinal, which we then read
                # levels = smutil.read_energy_levels(outputFilename)
                calc_tbmes = smutil.read_calc_tbme(outputFilename, self.tbme_template)
                calc_E = smutil.read_energy_levels(outputFilename)
            else: # Nothing exists for this nucleus, so we run it from scratch
                # nucleusSMC.run(is_mpi=self.is_mpi, n_restart_vec=n_restart_vec, max_lanc_vec=max_lanc_vec) 
                nucleusSMC.run(is_mpi=self.is_mpi) # n_restart_vec, max_lanc_vec set in initialization for tuning run
                # levels = smutil.read_energy_levels(os.path.join(rundirName, outputFilename))
                calc_tbmes = smutil.read_calc_tbme(os.path.join(rundirName, outputFilename), self.tbme_template)
                calc_E = smutil.read_energy_levels(os.path.join(rundirName, outputFilename))
                # Copy summary file to current step directory and remove current rundir
                shutil.copyfile(os.path.join(rundirName, outputFilename), outputFilename)
                #shutil.rmtree(rundirName) # May be commented out for debug
            
            # Transfer entries in calc_tbmes from current nucleus to total matrix for current run:
            # print calc_tbmes
            # for i in range(len(calc_tbmes[:,0])):
            #     calc_tbme_matrix[i_level,:] = calc_tbmes[i,:]
            #     i_level += 1
            calc_dict[nucleusName] = {"calc_tbme":calc_tbmes, "calc_E":calc_E} # Make dictionary containing both energy levels and tbme expectation values for current nucleus.
                                                                                                                                                 # calc_tbme have the same ordering as calc_E by construction

            # clean up
        os.chdir("../../") # Exit current fname_currentstepdir and steps folder

        # 20180116: Adding an option to remove the complete current fname_currentstepdir, to avoid using a lot of storage. This means all information we store is the PyMC3 trace. Not sure it's the best solution.
        # shutil.rmtree(os.path.join(self.fname_allstepsdir, fname_currentstepdir))


        return calc_dict

    def print_nuclei(self):
        for nucleusName, nucleusSettings in self.nucleiList.items():
            print(nucleusName)








# === Implement chisquare into a Theano Op class: ===
class ChiSquare(th.tensor.Op):

        itypes = [th.tensor.dvector]
        otypes = [th.tensor.dscalar]

        def __init__(self, core, model_space, spe_template, tbme_template, nucleiList, kshell_dir, expLevelsDict, mass_scaling=False, scaling_A0=0, scaling_p=0, is_mpi=False):
                self.core = core
                self.model_space = model_space
                self.spe_template = spe_template
                self.tbme_template = tbme_template
                self.nucleiList = nucleiList
                self.kshell_dir = kshell_dir
                self.expLevelsDict = expLevelsDict

                # Mass scaling parameters to be passed to interaction file. Only used if mass_scaling=True
                self.mass_scaling = mass_scaling
                self.scaling_A0 = scaling_A0
                self.scaling_p = scaling_p

                self.is_mpi = is_mpi

                
                self.step_sm = ShellModelEnsemble(self.core, self.model_space, self.spe_template, self.tbme_template, self.nucleiList, self.kshell_dir, mass_scaling=self.mass_scaling, scaling_A0=self.scaling_A0, scaling_p=self.scaling_p, is_mpi=self.is_mpi, max_lanc_vec=max_lanc_vec, n_restart_vec=n_restart_vec)

                # Derive useful constants:
                self.Nspe = len(self.model_space)
                self.Ntbme = len(tbme_template[:,0])

                self.Nparams = self.Nspe + self.Ntbme

                # Count number of experimental levels:                
                self.Nexp = 0
                for nucleusName in list(nucleiList.keys()):
                    self.Nexp += sum_num_levels(nucleiList[nucleusName]["levels"])





        def perform(self, node, inputs, outputs):
                spe_tbme, = inputs

                calc_dict = self.step_sm.run(spe_tbme) # Run KSHELL for the ensemble of nuclei. This is the money call!

                expLevelsDict = self.expLevelsDict

                chisquared = 0
                j_tol=1e-4

                for nucleusName in list(self.nucleiList.keys()):
                    # print "nucleus =", nucleusName
                    # Get experimental levels for current nucleus:
                    levels_experimental = expLevelsDict[nucleusName]["levels"]
                    sigma = expLevelsDict[nucleusName]["sigma"]
                    Egs_exp = expLevelsDict[nucleusName]["Egs"]
                    Ncompare = len(levels_experimental[:,0])

                    levels_calculated = calc_dict[nucleusName]["calc_E"]
                    # print("levels_calculated =", levels_calculated)
                    Egs_cal = levels_calculated[0,0]
                    levels_calculated[:,0] = levels_calculated[:,0] - Egs_cal # Take relative energies so the two levels_[] arrays are on the same footing
                    # Update 20171209: Changed the format of calc_tbme output, it's now a list of dictionaries containing {"E", "SPE", "TBME"} where the last two are matrices with all quantum numbers preserved

                    used_states = [] # List of experimental level indices that have been used
                    for i in range(Ncompare):
                        Ex_exp = levels_experimental[i,0]
                        J_exp = levels_experimental[i,1]
                        par_exp = levels_experimental[i,2]
                        # print "Exp:    Ex = {:f}, J = {:f}, par = {:f}".format(levels_experimental[i,0], levels_experimental[i,1], levels_experimental[i,2])
                        for j in range(len(levels_calculated[:,0])):
                            if np.abs(levels_calculated[j,1] - J_exp) < j_tol and par_exp==levels_calculated[j,2]:
                                if j not in used_states:
                                    chisquared += np.power(Ex_exp - levels_calculated[j,0], 2)/np.power(sigma[j],2) # Contribution from energy relative to ground state for each level

                                    used_states.append(j)
                                    break # Quit the j loop when we have found a match to current i.


                    # Add chisquare contribution from binding energy / ground state
                    chisquared += np.power(Egs_exp - Egs_cal, 2) / sigma[0]**2


     
                outputs[0][0] = np.array(chisquared)



        def grad(self, inputs, g):
                x, = inputs
                # TODO try to instantiate the ChiSquareGrad class in the __init__ of ChiSquare and call it via a self method, to avoid reinstantiating with every call?
                return [g[0]*ChiSquareGrad(self.core, self.model_space, self.spe_template, self.tbme_template, self.nucleiList, self.kshell_dir, self.expLevelsDict, self.mass_scaling, self.scaling_A0, self.scaling_p, self.is_mpi)(x)]



class ChiSquareGrad(th.tensor.Op):
        """
        Calculate the gradient of the chisquare

        """
        itypes = [th.tensor.dvector]
        otypes = [th.tensor.dvector]

        def __init__(self, core, model_space, spe_template, tbme_template, nucleiList, kshell_dir, expLevelsDict, mass_scaling=False, scaling_A0=0, scaling_p=0, is_mpi=False):
                self.core = core
                self.model_space = model_space
                self.spe_template = spe_template
                self.tbme_template = tbme_template
                self.nucleiList = nucleiList
                self.kshell_dir = kshell_dir
                # self.E_exp = E_exp
                # self.sigma = sigma
                self.expLevelsDict = expLevelsDict

                # Mass scaling parameters to be passed to interaction file. Only used if mass_scaling=True
                self.mass_scaling = mass_scaling
                self.scaling_A0 = scaling_A0
                self.scaling_p = scaling_p

                self.is_mpi = is_mpi
                self.step_sm = ShellModelEnsemble(self.core, self.model_space, self.spe_template, self.tbme_template, self.nucleiList, self.kshell_dir, mass_scaling=self.mass_scaling, scaling_A0=self.scaling_A0, scaling_p=self.scaling_p, is_mpi=self.is_mpi, max_lanc_vec=max_lanc_vec, n_restart_vec=n_restart_vec)

                # Derive useful constants:
                self.Nspe = len(self.model_space)
                self.Ntbme = len(tbme_template[:,0])

                # self.Nparams = 2 # Number of tuning parameters, for chisq dof
                self.Nparams = self.Nspe + self.Ntbme

                # Count number of experimental levels:                
                self.Nexp = 0
                for nucleusName in list(nucleiList.keys()):
                        self.Nexp += sum_num_levels(nucleiList[nucleusName]["levels"])

                # self.chisquare_grad_shared = th.shared(np.zeros(self.Nparams))

        def perform(self, node, inputs, outputs):
                spe_tbme, = inputs

                # Calculate $\sum_k \left( \frac{E_k^{exp} - \sum_i tbmes_i*calc_tbme_k,i}{sigma_k} \right)^2

                calc_dict = self.step_sm.run(spe_tbme)  # Run KSHELL for the ensemble of nuclei. This is the money call!


                expLevelsDict = self.expLevelsDict


                chisquare_gradient_x = np.zeros(self.Nspe+self.Ntbme)
                j_tol=1e-4

                for nucleusName in list(self.nucleiList.keys()):
                        # Get experimental levels for current nucleus:
                        levels_experimental = expLevelsDict[nucleusName]["levels"]
                        sigma = expLevelsDict[nucleusName]["sigma"]
                        Egs_exp = expLevelsDict[nucleusName]["Egs"]
                        Ncompare = len(levels_experimental[:,0])


                        levels_calculated = calc_dict[nucleusName]["calc_E"]
                        Egs_cal = levels_calculated[0,0]
                        levels_calculated[:,0] = levels_calculated[:,0] - Egs_cal # Take relative energies so the two levels_[] arrays are on the same footing
                        # Update 20171209: Changed the format of calc_tbme output, it's now a list of dictionaries containing {"E", "SPE", "TBME"} where the last two are matrices with all quantum numbers preserved
                        calc_tbme_dicts = calc_dict[nucleusName]["calc_tbme"]

                        # == ERROR TRAP: ==
                        # Test all levels to verify that sum(x_i*<O_i>) = <E>: (using the x_i of the summary files themselves)
                        tol_ctbme = 1e-2
                        for i_ctbme in range(len(calc_tbme_dicts)):
                            ctbme_absdiff = np.abs(calc_tbme_dicts[i_ctbme]["E"] \
                                - ((calc_tbme_dicts[i_ctbme]["SPE"][:,1]*calc_tbme_dicts[i_ctbme]["SPE"][:,2]).sum() \
                                     + (calc_tbme_dicts[i_ctbme]["TBME"][:,7]*calc_tbme_dicts[i_ctbme]["TBME"][:,8]).sum()) )
                            if not ctbme_absdiff < tol_ctbme:
                                raise Exception("sum(x_i*<O_i>) = <E> exceeds tolerance for nucleusName={:s}, level={:d}, abs(diff)={:f}".format(nucleusName, i_ctbme, ctbme_absdiff))
                        # == END ERROR TRAP ==

                        # Pick out ground state <SPE&TBME>. This needs to be subtracted with each gradient evaluation:
                        spe_expval_matrix_gs = calc_tbme_dicts[0]["SPE"]
                        spe_expval_matrix_gs = spe_expval_matrix_gs[np.argsort(spe_expval_matrix_gs[:,0]),:] # Check that SPEs are sorted by their orbital number
                        tbme_expval_matrix_gs = calc_tbme_dicts[0]["TBME"]
                        tbme_expval_matrix_gs = tbme_expval_matrix_gs[np.lexsort((tbme_expval_matrix_gs[:,4],tbme_expval_matrix_gs[:,3],tbme_expval_matrix_gs[:,2],tbme_expval_matrix_gs[:,1],tbme_expval_matrix_gs[:,0]))] # Check that tbmes are sorted by their quantum numbers in the same way as tbme_template
                        tbme_expect_calculated_gs = np.hstack((spe_expval_matrix_gs[:,2], tbme_expval_matrix_gs[:,8]))

                        used_states = [] # List of experimental level indices that have been used
                        for i in range(Ncompare):
                            Ex_exp = levels_experimental[i,0]
                            J_exp = levels_experimental[i,1]
                            par_exp = levels_experimental[i,2]
                            # print "Exp:    Ex = {:f}, J = {:f}, par = {:f}".format(levels_experimental[i,0], levels_experimental[i,1], levels_experimental[i,2])
                            for j in range(len(levels_calculated[:,0])):
                                if np.abs(levels_calculated[j,1] - J_exp) < j_tol and par_exp==levels_calculated[j,2]:
                                    if not j in used_states:


                                            spe_expval_matrix = calc_tbme_dicts[j]["SPE"]
                                            spe_expval_matrix = spe_expval_matrix[np.argsort(spe_expval_matrix[:,0]),:] # Check that SPEs are sorted by their orbital number
                                            tbme_expval_matrix = calc_tbme_dicts[j]["TBME"]
                                            tbme_expval_matrix = tbme_expval_matrix[np.lexsort((tbme_expval_matrix[:,4],tbme_expval_matrix[:,3],tbme_expval_matrix[:,2],tbme_expval_matrix[:,1],tbme_expval_matrix[:,0]))] # Check that tbmes are sorted by their quantum numbers in the same way as tbme_template
                                            tbme_expect_calculated = np.hstack((spe_expval_matrix[:,2], tbme_expval_matrix[:,8]))


                                            chisquare_gradient_x += ((Ex_exp - levels_calculated[j,0]) / sigma[j]**2 ) * (tbme_expect_calculated - tbme_expect_calculated_gs) # We multiply by -2 and normalize to Ndof at the end
                                            used_states.append(j)
                                            break # Quit the j loop when we have found a match to current i.


                        
                        # Add chisquare contribution from binding energy / ground state
                        chisquare_gradient_x += ((Egs_exp - Egs_cal) / sigma[0]**2) * tbme_expect_calculated_gs # We multiply by -2 and normalize to Ndof at the end



                chisquare_gradient = -2*chisquare_gradient_x#/max((self.Nexp-self.Nparams), 1) # Here we have the option to map from coordinates x to some subset of SPE&TBME parameter space

                outputs[0][0] = np.array(chisquare_gradient)#, dtype=node.outputs[0].dtype)







