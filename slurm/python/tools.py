# Just some useful tools.

import os
import sys
import math
import numpy as np
from functools import reduce
import operator
from path import Path
import netCDF4 as nc
from datetime import datetime

def print_time(message=""):
    """
    Used to time various processes. Prints the message and
    then the current time.
    """

    now = datetime.now()
    current_time = now.strftime("%H.%M:%S")

    print(message)
    print('Current time is '+ current_time)
    print()

def check_settings(settings_dict, key):
    """
    Checks an entry is in the settings dictionary and is not set to None.
    """

    if key in settings_dict:

        if settings_dict[key] is not None:
            return True

    return False

def get_absolute_path(directory):
    """
    Convert a relative directory path to an absolute one.
    """

    return os.path.abspath(directory)

def get_iteration_count(directory):
    """
    Counts the number of iterations in a directory. The iteration directories are
    assumed to have a name of the form iteration_x where x is an integer. 
    This is needed when collating results.
    """

    nruns = 0
    for root, dirs, files in os.walk(directory, topdown=False):
        subdirs = [ x for x in dirs if 'iteration_' in x ]
        nruns += len(subdirs)

    return nruns 

def set_in_dict(data_dict, map_list, value):
    """
    Sets item in dict given location as a list of string
    """

    get_from_dict(data_dict, map_list[:-1])[map_list[-1]] = value


def get_from_dict(data_dict, map_list):
    """
    Gets item in dict given location as a list of string
    """
    return reduce(operator.getitem, map_list, data_dict)

def add_parameter_key(parameter_map,
                      parameter_key=None,
                      parameter_attr=None,
                      parameter_location=None):
    """
    Generates a parameter key dictionary for reading data of interest
    from pyro objects.

    parameter_map     : Dictionary containing variable information
    parameter_key     : string to access variable
    parameter_attr    : string of attribute storing value in pyro
    parameter_location: list of strings showing path to value in pyro
    """

    if parameter_key is None:
        raise ValueError('Need to specify parameter key')

    if parameter_attr is None:
        raise ValueError('Need to specify parameter attr')

    if parameter_location is None:
        raise ValueError('Need to specify parameter location')

    dict_item = {parameter_key : [parameter_attr, parameter_location]}

    parameter_map.update(dict_item)

def create_parameter_keys():
    """
    Loads default parameters name into parameter_map

    {param : ["attribute", ["key_to_location_1", "key_to_location_2" ]] }

    for example

    {'electron_temp_gradient': ["local_species", ['electron','a_lt']] }
    """

    parameter_map = {}

    # ky
    # Note that ky in the output is normalised differently to the input aky.
    # To get the same value scale this by sqrt(2). This is to do with ensuring
    # consistency with CGYRO.
    parameter_key = 'ky'
    parameter_attr = 'numerics'
    parameter_location = ['ky']
    add_parameter_key(parameter_map, parameter_key, parameter_attr, parameter_location)

    # Electron temperature
    parameter_key = 'electron_temp'
    parameter_attr = 'local_species'
    parameter_location = ['electron', 'temp']
    add_parameter_key(parameter_map, parameter_key, parameter_attr, parameter_location)

    # Electron temperature gradient
    parameter_key = 'electron_temp_gradient'
    parameter_attr = 'local_species'
    parameter_location = ['electron', 'a_lt']
    add_parameter_key(parameter_map, parameter_key, parameter_attr, parameter_location)

    # Electron density gradient
    parameter_key = 'electron_dens_gradient'
    parameter_attr = 'local_species'
    parameter_location = ['electron', 'a_ln']
    add_parameter_key(parameter_map, parameter_key, parameter_attr, parameter_location)

    # Electron collisionality
    parameter_key = 'electron_nu'
    parameter_attr = 'local_species'
    parameter_location = ['electron', 'nu']
    add_parameter_key(parameter_map, parameter_key, parameter_attr, parameter_location)

    # Deuterium temperature
    parameter_key = 'deuterium_temp'
    parameter_attr = 'local_species'
    parameter_location = ['ion1', 'temp']
    add_parameter_key(parameter_map, parameter_key, parameter_attr, parameter_location)

    # Deuterium temperature gradient
    parameter_key = 'deuterium_temp_gradient'
    parameter_attr = 'local_species'
    parameter_location = ['ion1', 'a_lt']
    add_parameter_key(parameter_map, parameter_key, parameter_attr, parameter_location)

    # Deuterium density gradient
    parameter_key = 'deuterium_dens_gradient'
    parameter_attr = 'local_species'
    parameter_location = ['ion1', 'a_ln']
    add_parameter_key(parameter_map, parameter_key, parameter_attr, parameter_location)

    # Deuterium collisionality
    parameter_key = 'deuterium_nu'
    parameter_attr = 'local_species'
    parameter_location = ['ion1', 'nu']
    add_parameter_key(parameter_map, parameter_key, parameter_attr, parameter_location)

    # Rho 
    parameter_key = 'rho'
    parameter_attr = 'local_geometry'
    parameter_location = ['rho']
    add_parameter_key(parameter_map, parameter_key, parameter_attr, parameter_location)

    # Rmaj
    parameter_key = 'rmaj'
    parameter_attr = 'local_geometry'
    parameter_location = ['Rmaj']
    add_parameter_key(parameter_map, parameter_key, parameter_attr, parameter_location)

    # Kappa
    parameter_key = 'kappa'
    parameter_attr = 'local_geometry'
    parameter_location = ['kappa']
    add_parameter_key(parameter_map, parameter_key, parameter_attr, parameter_location)

    # Triangularity
    parameter_key = 'tri'
    parameter_attr = 'local_geometry'
    parameter_location = ['tri']
    add_parameter_key(parameter_map, parameter_key, parameter_attr, parameter_location)

    # q
    parameter_key = 'q'
    parameter_attr = 'local_geometry'
    parameter_location = ['q']
    add_parameter_key(parameter_map, parameter_key, parameter_attr, parameter_location)

    # shat
    parameter_key = 'shat'
    parameter_attr = 'local_geometry'
    parameter_location = ['shat']
    add_parameter_key(parameter_map, parameter_key, parameter_attr, parameter_location)

    # beta_prime
    parameter_key = 'beta_prime'
    parameter_attr = 'local_geometry'
    parameter_location = ['beta_prime']
    add_parameter_key(parameter_map, parameter_key, parameter_attr, parameter_location)

    # beta
    parameter_key = 'beta'
    parameter_attr = 'local_geometry'
    parameter_location = ['beta']
    add_parameter_key(parameter_map, parameter_key, parameter_attr, parameter_location)

    return parameter_map

def load_param_dict(filename='params.in'):
    """
    Loads a file containing parameter data.
    Expected format is a set of lines for the form:
    param name min_val max_val
    """

    param_dict = {}
    with open(filename) as fhandle:

        for line in fhandle:

            words = line.strip().split()
            if len(words) < 3:
                print('Invalid line encountered in '+filename)
                sys.exit(-1)

            param_dict[ words[0] ] = {}
            
            param_dict[ words[0] ]['min'] = float(words[1])
            param_dict[ words[0] ]['max'] = float(words[2])

            # If making a regular hypercube need n for each dimension
            if len(words) == 4:
                param_dict[ words[0] ]['n'] = int(words[3])
 
    return param_dict

def load_param_dict_with_set_values(filename='params.in'):
    """
    Loads a file containing parameter data.
    Expected format is a set of lines for the form:
    param_name val1 val2 val3 .... valn
    
    Used to generate n runs with prescribed values when 
    performing sequential design studies. 
    """

    parameter_dict = {}
    parameter_keys = []
    parameter_data = []

    # Number of new iterations to generate
    n_iterations = -1

    with open(filename) as fhandle:

        for line in fhandle:

            words = line.strip().split()
            if len(words) < 2:
                raise Exception('Invalid line encountered in '+filename)

            # Check each row has the same number of iterations
            if n_iterations > 0 and (len(words)-1) != n_iterations:
                raise Exception('Inconsistent number of entries for different parameters.')
            n_iterations = len(words) - 1

            key = words[0]
            parameter_keys.append(key)
            parameter_dict[key] = {}            
            parameter_dict[key]['values'] = []
            
            for i in range( len(words) - 1 ):
                parameter_dict[key]['values'].append( float(words[i+1]) )

            parameter_data.append( parameter_dict[key]['values'] )
 
    # Convert parameter_data to a numpy array with shape (nruns,1)
    parameter_data = np.array( parameter_data ).T

    print(f'Generating {n_iterations} new iterations from file.')

    return parameter_dict, parameter_keys, parameter_data

def generate_parameter_dictionary(keys,values):
    """
    Takes lists of parameter keys and corresponding values
    and converts them to a dictionary of key value pairs.
    """

    # Convert both to lists in case one is passed
    # as a numpy array
    keys_   = list(keys)
    values_ = list(values)

    # Check arrays are of equal length
    assert len(keys_) == len(values_)

    # Create dictionary
    pdict = {}
    for i in range(len(keys)):
        pdict[ keys_[i] ] = float( values[i] )

    return pdict

def get_output_dataset(pyro):
    """
    Reads the netcdf file corresponding to a pyro object.
    """

    # Read dataset
    netcdf_file_name = Path(pyro.run_directory + os.sep + pyro.file_name).with_suffix('.out.nc')
    return nc.Dataset(netcdf_file_name)

def read_single_value_file(datafile, dtype='float'):
    """
    Read a list of data values from a simple text file. Used to 
    read correlation length data or values of the glo parameter.
    """

    data = []
    with open(datafile) as gf:

        for line in gf:

            if dtype == 'float':
                data.append( float(line.strip()) )
            elif dtype == 'int':
                data.append( int(line.strip()) )
            else:
                raise Exception('Unknown data type when reading data file.')

    return np.array(data)

def remove_nans(parameters,targets):
    """
    Removes entries from parameter and target data arrays if either entry
    contains a nan or inf value (usually the targets). 
    Returns new arrays and the new size.
    """
    
    new_params  = []
    new_targets = []
    
    assert parameters.shape[0] == targets.shape[0]
    
    for i in range(parameters.shape[0]):
        
        parameters_ = list(parameters[i])
        targets_    = list(targets[i])
        
        tmp   = parameters_ + targets_
        clean = all([ not math.isnan(x) and not math.isinf(x) for x in tmp ])
        
        if clean:

            new_params.append(parameters_)
            new_targets.append(targets_)

    return np.array( new_params ), np.array( new_targets ), np.array( new_params ).shape[0] 

def remove_nans_converged(parameters,targets,converged,mtm):
    """
    Removes entries from parameter, target, converged and mtm data arrays if either entry
    contains a nan or inf value (usually the targets). Returns new arrays and the new size.
    """
    
    new_params    = []
    new_targets   = []
    new_converged = []
    new_mtm       = []
    
    assert parameters.shape[0] == targets.shape[0]
    assert parameters.shape[0] == converged.shape[0]
    assert parameters.shape[0] == mtm.shape[0]
    
    for i in range(parameters.shape[0]):
        
        parameters_ = list(parameters[i])
        targets_    = list(targets[i])
        
        tmp   = parameters_ + targets_ + [ converged[i], mtm[i] ]
        clean = all([ not math.isnan(x) and not math.isinf(x) for x in tmp ])
        
        if clean:

            new_params.append(parameters_)
            new_targets.append(targets_)
            new_converged.append( converged[i] )
            new_mtm.append( mtm[i] )

    return np.array( new_params ), np.array( new_targets ), np.array( converged ), np.array( mtm ), \
        np.array( new_params ).shape[0] 
