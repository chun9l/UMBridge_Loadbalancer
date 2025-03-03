import os
import time
import submission
from tools import generate_default_settings


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
                 directory           = './',
                 settings_dictionary = None,
                 sleep_time = 0.01):
        """
        Constructor for batch class.
        """
        
        self.sleep_time = sleep_time
        # Top level run directory
        self.directory = directory

        # Settings dict
        self.settings_dictionary = settings_dictionary
        if self.settings_dictionary is None:
            self.settings_dictionary = generate_default_settings()

        # List of iteration objects
        self.iterations = []


    def run(self):
        """ 
        Submits the batch of GS2 runs.
        """
        
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
                    time.sleep(self.sleep_time)



