from pyrokinetics import Pyro
import os
import numpy as np
import docker
import submission
from tools import *

class iteration():

    def __init__(self,
                 directory,
                 settings_dictionary,
                 gs2_template         = None,
                 parameter_dictionary = None,
                 batch_file = None):

        # Potentially set on initialisation
        self.directory            = get_absolute_path(directory)    # Directory for this iteration
        self.gs2_template         = gs2_template                    # Template input file
        self.parameter_dictionary = parameter_dictionary            # Dictionary of parameters to change  
        self.settings_dictionary  = settings_dictionary             # Settings dictionary
        self.batch_file = batch_file

        # Other data which will be set later
        self.pyro                 = None
        self.process_id           = None
        self.output_data          = None

        # Completion data
        self.completed            = None  # Run completed (did not crash)
        self.ftime                = None  # Final time
        self.nstep                = None  # Number of completed steps
        self.timeout              = None  # Run timed out (completed nsteps)
        self.crashed              = False # True if netcdf does not exist - i.e. complete failure.

        # Get pyro keys dictionary
        self.pyro_keys = create_parameter_keys()

        # If there is a template and a parameter dictionary create a pyro object
        if gs2_template is not None and parameter_dictionary is not None:
            self.generate_pyro_object()

        # GS2 input file name to use
        self.input_file_name_short = 'gs2.in'
        self.input_file_name = self.directory + os.sep + 'gs2.in'

        # GS2 output file name
        self.output_file_name = self.directory + os.sep + 'gs2.out.nc'

        # Parameter file name to use
        self.param_file_name = self.directory + os.sep + 'params.dat'

    # Top level functions -------------------------------

    def run_iteration(self):
        """
        Submit a run of GS2 once a folder has been set up.
        """

        # Don't submit a job if in test mode
        if self.settings_dictionary['test_mode']:
            return

        if self.settings_dictionary['use_containers'] is True:

            # Submit container when cores are available
            docker.run_docker(self.directory, self.input_file_name_short, self.settings_dictionary)


        else:
            
            self.process_id = submission.submit_batch_job(self.directory, self.input_file_name_short, self.settings_dictionary, self.batch_file)


