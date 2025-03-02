import submission
import os


class iteration():

    def __init__(self,
                 directory,
                 settings_dictionary,
                 batch_file = None):

        # Potentially set on initialisation
        self.directory            = os.path.abspath(directory)      # Directory for this iteration
        self.settings_dictionary  = settings_dictionary             # Settings dictionary
        self.batch_file = batch_file

        # Other data which will be set later
        self.process_id           = None

    # Top level functions -------------------------------

    def run_iteration(self):
        """
        Submit a run of GS2 once a folder has been set up.
        """

        # Don't submit a job if in test mode
        if self.settings_dictionary['test_mode']:
            return
        
        self.process_id = submission.submit_batch_job(self.directory, self.settings_dictionary, self.batch_file)


