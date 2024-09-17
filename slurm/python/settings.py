# Generates default settings dictionary

def generate_default_settings():

    # Settings dictionary
    settings = {}

    # Use containers instead of batch submission
    settings['use_containers'] = False

    # Averaging window at end of run for calculating frequency
    # and growth rate : [ x : 1.0 ] * t_end
    settings['window_minimum'] = 0.8

    # Run Settings =============================

    # Cores per job
    settings['ncores'] = 16

    # Cores per node - 56 for cclake, 32 for skylake 
    settings['cores_per_node'] = 56

    # Image name when using docker 
    settings['image'] = 'gs2_local'

    # Max number of simultaneous jobs
    settings['max_runs'] = 20

    # Not a test
    settings['test_mode'] = False

    # MTM Definition ===========================

    # Default settings check frequency and tearing parameter.

    # Minimum tearing parameter
    settings['check_tearing'] = True
    settings['min_tearing_parameter'] = 0.01
    
    # Minimum ratio of Apar to Phi
    settings['check_apar_phi_ratio'] = False
    settings['min_apar_phi_ratio'] = 0.2

    # Minimum ratio of integral of Apar dtheta to integral of Phi dtheta
    settings['check_apar_phi_integral_ratio'] = False
    settings['min_apar_phi_integral_ratio']   = 0.2

    # Frequency checks
    settings['check_frequency_sign']     = True
    settings['check_expected_frequency'] = True

    # Maximum fractional variation of frequency from expected value
    settings['frequency_window'] = 0.5

    # Convergence tolerance ====================
    settings['tolerance_navg'] = 50
    settings['max_tolerance'] = 1.0e-3

    # Miscellaneous settings ===================

    # Print diagnostic messages
    settings['print_messages'] = True

    return settings
