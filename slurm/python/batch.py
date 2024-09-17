import os
import numpy as np
import time
import submission
from iteration import iteration
from settings import generate_default_settings
from tools import get_iteration_count
from tools import create_parameter_keys
from tools import generate_parameter_dictionary
from tools import remove_nans

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


