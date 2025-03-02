# Just some useful tools.

import os

def generate_default_settings():

    # Settings dictionary
    settings = {}

    # Max number of simultaneous jobs
    settings['max_runs'] = 10

    # Not a test
    settings['test_mode'] = False

    return settings

def generate_iteration_dir(base_dir, num_iter):
    abs_root_path = os.path.abspath(base_dir)
    os.chdir(abs_root_path)
    for i in range(num_iter):
        os.system(f"mkdir -p iteration_{i}")