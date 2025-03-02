# Tools for handling job submission on DIRAC
import re
import os
import subprocess 


def count_active_jobs(process_ids):
    """
    Given a list of process ids for submitted batch
    jobs determines how many are still running and 
    returns an updated list of ids.
    """

    assert type(process_ids) == list 

    # Read data from squeue into buffer
    command = 'squeue'
    command_buffer = os.popen(command).read()

    # Identify which processes are still active
    states = [ True if str(x) in command_buffer else False for x in process_ids ]

    # Get updated list of process ids
    new_ids = [ x for x,y in zip(process_ids,states) if y is True ]

    # Return number of active jobs and new list of active ids
    return len(new_ids), new_ids


def can_run_job(process_ids, max_jobs):
    """
    Currently just imposes a maximum number of jobs.
    """
    
    assert type(process_ids) == list

    if( len(process_ids) >= max_jobs ):
        return False

    return True

# 'PUBLIC' Functions ==============================

def submit_batch_job(run_directory, settings, batch_file):
    """
    Submits a batch job to execute GS2 in run_directory

    run_directory : Directory in which to execute code 
    file_name     : Name of GS2 input file
    settings      : Settings dictionary
    """

    # Number of cores per job
    cores = settings['ncores']
    
    # Sets the path to batch file
    target   = run_directory + os.sep + batch_file

    # Submit job and recover process ID
    cmnd   = "sbatch " + target
    result = str( subprocess.check_output(cmnd, shell=True,stderr=subprocess.STDOUT) )

    # Get process ID of submitted job
    proc_id = None
    if 'Submitted batch job' in result:
        proc_id = int( re.sub("[^0-9]", "", result.strip() ) )
        print('Submitted job ' + str(proc_id) )

    return proc_id
