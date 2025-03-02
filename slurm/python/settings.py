# Generates default settings dictionary

def generate_default_settings():

    # Settings dictionary
    settings = {}

    # Max number of simultaneous jobs
    settings['max_runs'] = 10

    # Not a test
    settings['test_mode'] = False

    return settings
