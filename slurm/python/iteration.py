from pyrokinetics import Pyro
import os
import numpy as np
import netCDF4 as nc
import docker
import submission
import gpe_csv
from mtm import check_is_mtm
from tools import *

class iteration():

    def __init__(self,
                 directory,
                 settings_dictionary,
                 gs2_template         = None,
                 parameter_dictionary = None):

        # Potentially set on initialisation
        self.directory            = get_absolute_path(directory)    # Directory for this iteration
        self.gs2_template         = gs2_template                    # Template input file
        self.parameter_dictionary = parameter_dictionary            # Dictionary of parameters to change  
        self.settings_dictionary  = settings_dictionary             # Settings dictionary

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

    def generate_pyro_object(self):
        """
        Generates a pyro object for this iteration based on
        a template namelist and a dictionary of parameters to
        update.
        """

        if self.gs2_template is None or self.parameter_dictionary is None:
            print('Iteration object is missing input data!')
            print('Cannot instantiate pyro object.')
            return

        # Create pyro object
        self.pyro = Pyro(gk_file=self.gs2_template, gk_code='GS2')

        # Update data in pyro object based on parameter dictionary
        for param, value in self.parameter_dictionary.items():

            # Get attribute and keys where param is stored
            attr_name, keys_to_param, = self.pyro_keys[param]
            
            # Get dictionary storing the parameter
            param_dict = getattr(self.pyro, attr_name)
            
            # Set the value given the dictionary and location of parameter
            set_in_dict(param_dict, keys_to_param, value)

    def generate_run_folder(self):
        """
        Generates run data in a folder.
        """

        if self.pyro is None:
            self.generate_pyro_object()
            if self.pyro is None:
                return

        # Write an input file in the directory
        self.pyro.write_gk_file(self.input_file_name, template_file=self.gs2_template)

        # Create a restart directory
        os.system('mkdir -p '+self.directory+os.sep+'restart')

        # Copy data from existing restart directory if needed
        if check_settings(self.settings_dictionary, 'restart_dir'):

            # Add restart settings to namelist file
            if 'knobs' not in self.pyro.gs2_input:
                self.pyro.gs2_input['knobs'] = {}

            if 'init_g_knobs' not in self.pyro.gs2_input:
                self.pyro.gs2_input['init_g_knobs'] = {}

#            self.pyro.gs2_input['knobs']['delt_option']         = 'check_restart'
            self.pyro.gs2_input['init_g_knobs']['ginit_option'] = 'many'

            # Update namelist
            self.pyro.write_gk_file(self.input_file_name, directory=self.directory, template_file=self.gs2_template)
            
            # Create symlinks to contents of restart directory
            # Changing directories seems required to have symlinks point to the right place
            cwd = os.getcwd()
            restart_dir = cwd+os.sep+self.settings_dictionary['restart_dir']
            os.chdir(self.directory+os.sep+'restart')
            os.system('cp '+restart_dir+'/* .')
            os.chdir(cwd)

        # Copy data from directory with closest point in parameter space
        elif check_settings(self.settings_dictionary, 'restart_closest') and self.settings_dictionary['restart_closest']:

            # Check needed settings
            got_dir = check_settings(self.settings_dictionary, 'restart_top_dir')
            got_csv = check_settings(self.settings_dictionary, 'restart_batch_csv')

            if not (got_dir and got_csv):
                raise Exception('Insufficient data in settings to restart from closest run.')

            # restart_batch_csv sets a batch csv file of candidate iterations to use as templates
            parameter_names, parameter_values, target_names, target_values, converged, mtm = \
                gpe_csv.read_csv(self.settings_dictionary['restart_batch_csv'])

            # Read data on scale lengths
            if check_settings(self.settings_dictionary, 'scale_lengths'):
                scale_lengths = read_single_value_file( self.settings_dictionary['scale_lengths'] )
            else:
                scale_lengths = None

            # Read glo data to ensure run is compatible
            if check_settings(self.settings_dictionary,'glo_file') and check_settings(self.settings_dictionary,'glo_target'):
                glo       = read_single_value_file( self.settings_dictionary['glo_file'], dtype='int' )
                glotarget = int(self.settings_dictionary['glo_target'])
            else:
                glo       = None
                glotarget = None

            # Get new parameter values for this iteration
            new_parameters = self.get_parameters(parameter_names)

            # Find closest existing compatible iteration
            closest_index = self.find_nearest_mtm( new_parameters, parameter_values, mtm, scale_lengths=scale_lengths, \
                                                   glos=glo, glotarget=glotarget )

            # Add restart settings to namelist file
            if 'knobs' not in self.pyro.gs2_input:
                self.pyro.gs2_input['knobs'] = {}

            if 'init_g_knobs' not in self.pyro.gs2_input:
                self.pyro.gs2_input['init_g_knobs'] = {}

#            self.pyro.gs2_input['knobs']['delt_option']         = 'check_restart'
            self.pyro.gs2_input['init_g_knobs']['ginit_option'] = 'many'

            # Update namelist
            self.pyro.write_gk_file(self.input_file_name, directory=self.directory, template_file=self.gs2_template)

            # Create symlinks to contents of restart directory
            # Changing directories seems required to have symlinks point to the right place
            cwd = os.getcwd()
            restart_dir = self.settings_dictionary['restart_top_dir']+os.sep+'iteration_'+str(closest_index)+'/restart'

            os.chdir(self.directory+os.sep+'restart')
            os.system('cp '+restart_dir+'/* .')
            os.chdir(cwd)

        # Write a parameter file to indicate which data was varied
        self.save_parameter_dictionary()

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
            
            self.process_id = submission.submit_batch_job(self.directory, self.input_file_name_short, self.settings_dictionary)

    def resubmit_iteration(self):
        """
        Resubmit a run of GS2 in a folder with a restart directory.
        """

        if 'knobs' not in self.pyro.gs2_input:
            self.pyro.gs2_input['knobs'] = {}

        if 'init_g_knobs' not in self.pyro.gs2_input:
            self.pyro.gs2_input['init_g_knobs'] = {}

#        self.pyro.gs2_input['knobs']['delt_option']         = 'check_restart'
        self.pyro.gs2_input['init_g_knobs']['ginit_option'] = 'many'

        # Rewrite input file
        self.pyro.write_gk_file(self.input_file_name, directory=self.directory, template_file=self.gs2_template)

        # Rerun job
        self.run_iteration()

    def initialise_from_folder(self,check_mtm=True):
        """
        Initialise the iteration object from an existing folder.
        """

        # Set actual input file as template
        self.gs2_template = self.input_file_name
        
        # Read parameter dictionary
        self.read_parameter_dictionary()

        # Create pyro object
        self.pyro = Pyro(gk_file=self.gs2_template, gk_type='GS2')

        # If output file exists read output data
        if os.path.isfile(self.output_file_name):
            self.read_output_data(check_mtm=check_mtm)

    def read_output_data(self,check_mtm=True):
        """
        Read output data from a completed iteration into object.
        """
        
        print()
        print('Reading output data for run in directory: ')
        print(self.directory)
        print()

        # Check netcdf file exists 
        exists = self.check_netcdf_exists()
        if not exists:
            print( f'NETCDF FILE DOES NOT EXIST!' )
            print()
            return

        # Read output data
        self.pyro.gk_code.load_grids(self.pyro)
        self.pyro.gk_code.load_fields(self.pyro)
        self.pyro.gk_code.load_eigenvalues(self.pyro)

        # Get full netcdf dataset
        self.output_data = nc.Dataset(self.output_file_name)

        # Get frequency and growth rate
        self.get_targets()

        # Get convergence tolerance 
        self.get_tolerance()

        print( f'Calculated frequency   = {self.targets[0]}')
        print( f'Calculated growth rate = {self.targets[1]}')
        print()
        print( f'Growth rate tolerance  = {self.tolerance}' )
        print( f'Frequency tolerance    = {self.frequency_tolerance}' )
        print()

        # Get final time and whether run properly completed
        self.get_final_time()
        self.run_completed()
        print( f'Run finished at {self.ftime} after {self.nstep} steps. Completed = {self.completed}')
        print()

        if not self.completed:
            print('RUN CRASHED / HIT WALLTIME LIMIT')

        if self.stopped:
            print('RUN HIT NSTEPS')

        # Set convergence flag ---------------
        self.converged = self.completed and not self.stopped
        if self.converged:
            print('RUN CONVERGED.')
        else:
            print('RUN NOT CONVERGED.')
        print()

        # Check if this is an mtm
        if check_mtm:
            self.is_mtm = check_is_mtm(self)
  
    def get_parameter_dictionary(self):
        """
        Just returns the parameter directionary.
        """

        return self.parameter_dictionary

    def get_parameters(self,param_names):
        """
        Returns an array of the input parameters with names given
        by param_names.

        param_names : A list of parameter names to return the values of
        """

        parameters = []

        # Get varied parameter data
        for param in param_names:

            # Get attribute and keys where param is stored
            attr_name, key_to_param, = self.pyro_keys[param]

            # Get dictionary storing the parameter
            param_dict = getattr(self.pyro, attr_name)

            # Get the required value given the dictionary and location of parameter
            value = get_from_dict(param_dict, key_to_param)

            parameters.append(value)

        return np.array(parameters)

    def get_targets(self):

        """
        Returns a numpy array containing the frequency and growth rate averaged
        over a window at the end of the run:
        
        Averaging time window = [window_minimum:1.0] * t_end
    
        """

        exists = self.check_netcdf_exists()
        if self.crashed:
            return np.array([0.0,0.0])

        targets    = []

        # Get output data
        if self.output_data is None:
            self.read_output_data()

        output_data = self.pyro.gk_output.data
        
        frequency   = output_data['mode_frequency']
        growth_rate = output_data['growth_rate']

        final_time = growth_rate['time'].isel(time=-1)

        window_minimum = self.settings_dictionary['window_minimum']

        targets.append( np.mean(   frequency.where(   frequency.time > window_minimum * final_time ) ) )
        targets.append( np.mean( growth_rate.where( growth_rate.time > window_minimum * final_time ) ) )

        self.targets = np.array(targets)
        return self.targets

    # Helper functions ----------------------------------

    def save_parameter_dictionary(self):
        """
        Write the parameter dictionary data into a file in
        the given directory so it can be recovered later.
        """

        with open( self.param_file_name, 'w' ) as param_file:

            for param, value in self.parameter_dictionary.items():

                line = param + ' ' + str(value) + '\n'
                param_file.write(line)

    def read_parameter_dictionary(self):
        """
        Read a parameter file in the given directory into 
        the object. Used when recovering an object from a 
        run folder.
        """

        self.parameter_dictionary = {}

        with open( self.param_file_name, 'r' ) as param_file:

            for line in param_file:

                words = line.strip().split()

                if len(words) != 2:
                    print('Incorrectly formatted parameter file line. Skipping.')
                    continue

                self.parameter_dictionary[words[0]] = float(words[1])

    def check_netcdf_exists(self):
        """
        Checks that the netcdf file exists and sets the run
        as unconverged if not.
        """

        exists = os.path.exists(self.output_file_name)

        if not exists:

            self.completed = False
            self.stoped    = False
            self.converged = False
            self.tolerance = 0.0
            self.frequency_tolerance = 0.0
            self.targets   = np.array( [0,0] )
            self.is_mtm    = False
            self.crashed   = True
            self.frequency_ratio = 0.0
            self.tearing_parameter = 0.0
            self.ftime             = -1.0
            self.nstep             = -1
    
        return exists

    # Functions for determining if the iteration has converged / timed out / crashed

    def get_final_time(self):
        """
        Returns the final simulation time.
        Also checks if the run timed out (was stopped by system). 
        Time from pyro is in wstar units normalised by ky.
        Data is only written every nwrite steps so need to correct nsteps for this.
        """

        # Get input nstep, nwrite and ky
        nstep  = self.pyro.gs2_input['knobs']['nstep']                  # Maximum number of timesteps
        nwrite = self.pyro.gs2_input['gs2_diagnostics_knobs']['nwrite'] # Output is written every nwrite steps
        ky     = self.pyro.gs2_input['kt_grids_single_parameters']['aky']

        # Correct for sqrt(2) factor
        ky = ky / ( 2.0**0.5 )

        # Get final time and number of timesteps
        self.ftime = self.pyro.gk_output.time[-1] * ky
        self.nstep = ( self.pyro.gk_output.time.size - 1 ) * nwrite

        # Did the run hit max nstep
        self.stopped = self.nstep >= nstep
        
    def run_completed(self):
        """
        Checks the run completed by checking exit_reason.
        Does not imply convergence, the run may have finished nsteps.
        """

        self.completed = False
        with open(self.directory+os.sep+'gs2.exit_reason','r') as fh:

            text = fh.read()
            self.completed = 'completed' in text

        return self.completed

    def force_good_run(self):
        """
        Specify that this run is good and should be used as a valid MTM.
        """

        self.converged = True
        self.is_mtm    = True

    def get_variable_tolerance(self, variable):
        """
        Returns the convergence tolerance of a variable.
        The condition gs2 appears to use is to demand the standard error on the
        mean value is less than the set tolerance (omegatol) multiplied
        by the lesser of 1 or the average value where the averages are calculated
        over navg steps. 
        """

        # Average over final navg time points
        window = min([ self.settings_dictionary['tolerance_navg'], variable.size])

        # Get data from specified window
        variable_window = variable.isel(time=np.arange(-1*window,0)).isel(ky=0)

        # Get average over window
        variable_avg = float(np.mean(variable_window))

        # Get squared differences from average
        difference = (variable_window.data - variable_avg)**2.0

        # Get standard deviation
        standard_deviation = ( abs( np.sum(difference) ) / window )**0.5

        # Get normalisation
        norm = min( abs(variable_avg), 1.0 )

        # Tolerance = relative standard error on mean growth rate
        tolerance = standard_deviation / norm

        return tolerance

    def get_tolerance(self):
        """
        Returns the growth rate and frequency tolerances.
        """

        # Get calculated growth rate and frequency
        growth_rate = self.pyro.gk_output.data['growth_rate']
        frequency   = self.pyro.gk_output.data['mode_frequency']

        # Calculate tolerances
        self.tolerance           = self.get_variable_tolerance(growth_rate)
        self.frequency_tolerance = self.get_variable_tolerance(frequency)

        # Save tolerance in pyro object
        self.pyro.gk_output.data['growth_rate_tolerance'] = self.tolerance

    def get_tolerance_old(self):
        """
        Returns the growth rate tolerance.
        Version of this function that matches Bhavin's pyrokinetics calculation
        but using navg points as per GS2. 
        """

        growth_rate = self.pyro.gk_output.data['growth_rate']

        final_growth_rate = growth_rate.isel(time=-1).isel(ky=0)

        difference = abs(growth_rate - final_growth_rate) / final_growth_rate

        # Average over final navg time points
        window = min([ self.settings_dictionary['tolerance_navg'], difference.size])

        self.tolerance = abs(float(np.mean(difference.isel(time=np.arange(-1*window,0)))))
        self.pyro.gk_output.data['growth_rate_tolerance'] = self.tolerance

        print( growth_rate.isel(time=np.arange(-1*window,0)) )
        print( difference.isel(time=np.arange(-1*window,0)) )

    def find_nearest_mtm( self, new_parameters, existing_parameters, existing_mtm, scale_lengths=None, glos=None, glotarget=None ):
        """
        Finds the nearest MTM in parameter space to a specified new set of parameters.
        Used for finding the best template run for a new run.

        existing_mtm is a set of flags indicating if the existing runs being surveyed
        have been identified as converged mtms.
        """

        # Indices of good mtms and squared distances from new points
        # 0 index required as where returns a tuple containing a np array

        if glos is None or glotarget is None:
            indices  = np.where( existing_mtm == 1 )[0]
        else:
            assert glos.size == existing_mtm.size
            indices  = np.where( existing_mtm == 1 and glos == glotarget )[0]

        distance = []

        # Loop over good MTMs
        for run in indices:

            dist2 = 0
            for ip in range( new_parameters.size ):

                d2 = ( new_parameters[ip] - existing_parameters[run,ip] )**2.0

                # Normalise to correlation length
                if scale_lengths is not None:
                    d2 = d2 / scale_lengths[ip]**2.0

                dist2 = dist2 + d2

            distance.append(dist2)

        # Sort indices by distance
        sorted_dists, sorted_indices = zip(*sorted(zip(np.array(distance),indices)))

        print(f'Closest existing point is iteration {sorted_indices[0]} at squared distance {sorted_dists[0]}')

        # Return index of closest iteration
        return sorted_indices[0]
