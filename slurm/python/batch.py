import os
import numpy as np
import time
import submission
from iteration import iteration
from gpe_csv import *
from settings import generate_default_settings
from tools import get_iteration_count
from tools import create_parameter_keys
from tools import generate_parameter_dictionary
from tools import remove_nans
from plot import plot_suite

# A class for creating and interacting with a batch of GS2 runs
# created using a template input file and a dictionary of parameter
# values.

class batch():
    """
    template_file : The name of a GS2 input file to use as a template
    directory     : The top level run directory
    settings      : Settings dictionary
    parameters    : The dictionary of parameters data to change
    """

    def __init__(self, 
                 template_file,
                 directory           = './',
                 settings_dictionary = None,
                 parameter_keys      = None,
                 parameter_data      = None,
                 batch               = False):
        """
        Constructor for batch class.
        """

        # Top level run directory
        self.directory = directory

        # Template input file to use
        self.template_file = template_file

        # Settings dict
        self.settings_dictionary = settings_dictionary
        if self.settings_dictionary is None:
            self.settings_dictionary = generate_default_settings()

        # Parameter information.
        self.parameter_keys = parameter_keys    # List of key names of parameters to vary
        self.parameter_data = parameter_data    # Numpy array (nruns,nkeys) containing varied parameter data.

        # Running under a batch system?
        self.batch = batch

        # Target names
        self.target_names   = ['mode_frequency','growth_rate']

        # Number of iterations to generate
        self.n_iterations = None

        # List of iteration objects
        self.iterations = []

        # Get pyro keys dictionary
        self.pyro_keys = create_parameter_keys()

    def write_batch(self):
        """
        Generates a folder structure based on the template file and the
        parameter information stored in the batch class. 
        """

        if self.parameter_keys is None or self.parameter_data is None:
            print('No available parameter information. Cannot generate batch.')
            return

        self.n_iterations = self.parameter_data.shape[0]
        print('Generating '+str(self.n_iterations)+' GS2 runs.')

        # Check if parameters are in viable options
        for key in self.parameter_keys:
            if key not in self.pyro_keys.keys():
                raise ValueError(f'Key {key} has not been loaded into pyro_keys')
                return

        # Copy template file into top directory
        os.system('cp '+self.template_file+' '+self.directory)

        # Reset iteration list
        self.iterations = []

        # Iterate through all runs, generate iterations and folders
        for run in range(self.n_iterations):

            # Construct parameter dictionary
            parameter_dict = generate_parameter_dictionary( self.parameter_keys,
                                                            self.parameter_data[run] )

            # Create file name for each run
            iteration_directory = self.directory + os.sep + 'iteration_'+str(run)

            # Create iteration object for this run
            self.iterations.append( iteration(iteration_directory,
                                              self.settings_dictionary,
                                              self.template_file,
                                              parameter_dict ) )

            # Write folder for this iteration
            self.iterations[-1].generate_run_folder()

    def run(self, iteration_list=None):
        """ 
        Submits the batch of GS2 runs.
        """
        
        if iteration_list is None:

            process_ids = []
            for iteration in self.iterations:
                os.chdir(iteration.directory)
                print(f"changing to {iteration.directory}")
                while True:
                    if submission.can_run_job(process_ids, self.settings_dictionary["max_runs"]):
                        iteration.run_iteration()
                        process_ids.append(iteration.process_id)
                        break
                    else:
                        num_active_jobs, process_ids = submission.count_active_jobs(process_ids)
                        time.sleep(1)


        else:

            for iteration in iteration_list:
                self.iterations[iteration].run_iteration()

    def resubmit(self):
        """
        Resubmits any iterations which are not converged.
        """

        for iteration in self.iterations:
            iteration.resubmit_iteration()

    def read_output_data(self):
        """
        Reads output data for all iterations assuming that the runs are 
        completed.
        """

        for iteration in self.iterations:

            iteration.read_output_data()

    def get_parameter_and_target_names():
        """
        Returns parameter and target names.
        """
        return self.parameter_keys, self.target_names

    def get_parameters_and_targets(self,iterations,parameter_names,good_only=False):
        """
        Returns an array of the specified input and output values (frequency and growth rate)
        for the iterations. To get just the varied parameters set param_names = self.parameter_keys.

        To get all data use self.iterations for arg 2

        good_only = True results in only converged MTMs being included in the output.
        """

        parameters = []
        targets    = []

        # Iterate through all runs and recover output
        for iteration in iterations:

            if (not good_only) or (iteration.converged and iteration.is_mtm):

                parameters.append( list( iteration.get_parameters(parameter_names) ) )
                targets.append(    list( iteration.get_targets()                   ) )

        return np.array( parameters ), np.array( targets )

    def get_final_times(self,iterations):
        """
        Returns an array of the final simulation times of the iterations.
        """

        times = [ iteration.ftime for iteration in iterations ]
        return np.array( times )

    def get_final_step_count(self,iterations):
        """
        Returns an array of the total number of steps take by each of the iterations.
        """

        nsteps = [ float(iteration.nstep) for iteration in iterations ]
        return np.array( nsteps )

    def get_tolerances(self,iterations):
        """
        Returns an array of the convergence tolerances of the iterations.
        To get all data use self.iterations for arg 2
        """

        tolerances = [ iteration.tolerance for iteration in iterations ]
        return np.array( tolerances )

    def get_frequency_tolerances(self,iterations):
        """
        Returns an array of the frequency tolerances of the iterations.
        To get all data use self.iterations for arg 2
        """

        tolerances = [ iteration.frequency_tolerance for iteration in iterations ]
        return np.array( tolerances )

    def get_frequency_ratios(self,iterations):
        """
        Returns an array of the ratios of the calculated and expected
        frequencies of the iterations.
        To get all data use self.iterations for arg 2
        """

        ratios = [ iteration.frequency_ratio for iteration in iterations ]
        return np.array( ratios )

    def get_tearing_parameters(self):
        """
        Returns an array of the tearing parameters for the iterations.
        """

        tearing = [ iteration.tearing_parameter for iteration in self.iterations ]
        return np.array( tearing )

    def is_converged_mtm(self):
        """
        Returns an array of boolean flags indicating whether the 
        iterations found converged MTMs.
        """

        mtms = [ iteration.converged and iteration.is_mtm for iteration in self.iterations ]
        return mtms

    def force_converged_mtms(self,iterations):
        """
        iterations is a list of indices of iterations to set as converged MTMs.
        This will ensure they are included in future analysis.
        """

        for iteration in iterations:

            self.iterations[ int(iteration) ].force_good_run()

    def is_converged(self):
        """
        Returns an array of boolean flags indicating whether the 
        iterations converged.
        """
        
        converged = [ iteration.converged for iteration in self.iterations]
        return converged

    def ftime_and_nstep(self):
        """
        Returns the final simulation time and the total number of steps
        executed by the iterations.
        """

        ftime = [ iteration.ftime for iteration in self.iterations ]
        nstep = [ iteration.nstep for iteration in self.iterations ]

        return ftime, nstep

    def create_csv(self,iterations,parameter_names,filename='batch.csv',no_nans=False,good_only=False):
        """
        Creates a CSV file containing the specified parameter data and resulting 
        frequencies and growth rates from the selected iterations. The file is 
        created in the batch directory and called <filename>.
        """

        # Get data
        parameters, targets = self.get_parameters_and_targets(iterations,parameter_names,good_only=good_only)

        # Get convergence / mtm status
        converged = self.is_converged()
        mtm       = self.is_converged_mtm()

        # Get final time and number of steps
        ftime, nsteps = self.ftime_and_nstep()

        # Get frequency ratios and tearing parameters
        tearing = self.get_tearing_parameters()
        ratios  = self.get_frequency_ratios(self.iterations)

        # Append convergence / mtm data to targets
        output_names = self.target_names + [ 'converged', 'mtm', 'ftime', 'nsteps', 'tearing', 'frequency_ratio' ]

        # Construct output array
        outputs = np.array([ list(targets[x]) + [ converged[x], mtm[x], ftime[x], nsteps[x], tearing[x], ratios[x] ] for x in range(len(targets)) ])

        # Remove nan entries from the data 
        if no_nans:
            parameters, outputs, n_notnan = remove_nans(parameters,outputs)

        # Write the data file
        create_csv(self.directory, filename, parameter_names, parameters, output_names, outputs)

    def read_batch(self): 
        """ Recover a folder of data into a batch object."""

        # Count number of iterations in folder
        self.n_iterations = get_iteration_count(self.directory)

        # Reset iteration list
        self.iterations = []

        # Initialise parameter data
        self.parameter_keys = []
        self.parameter_data = []

        # Initialise iterations
        for run in range(self.n_iterations):

            # Directory name for this iteration
            iteration_directory = self.directory + os.sep + 'iteration_'+str(run)

            self.iterations.append( iteration( iteration_directory, self.settings_dictionary ) )
            self.iterations[-1].initialise_from_folder()

            # Get parameter dictionary
            params = self.iterations[-1].get_parameter_dictionary()

            # Get parameter keys
            if run == 0:
                for key in params.keys():
                    self.parameter_keys.append(key)

            # Get parameter data
            data = []
            for key in self.parameter_keys:
                data.append( params[key] )

            self.parameter_data.append( data )
                    
        self.parameter_data = np.array( self.parameter_data )

    def plot(self,iterations, parameter_name):
        """
        Generates a suite of plots from the given set of iterations
        and the specified parameter name as X axis.
        """
        
        plot_suite(self, iterations, parameter_name)
