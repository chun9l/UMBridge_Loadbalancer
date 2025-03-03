This directory contains the code for the SLURM part of the experiments, where we use Python scripts to naiively `sbatch` jobs independent of UM-Bridge. These Python scripts were originally provided by our collaborators at UKAEA, and have been heavily modified for this work.

We recommend creating a new directory for each testcase you run as we will generate a sub-folder for every job submitted to store the SLURM output and ID. 

The scripts that run the benchmarks are named "run-*-batch.py". It streamlines the process of submitting SLURM jobs, you can specify your batch file in there and how many concurrent jobs allowed in the queue. Note that you will need to build GS2 for its benchmark.

settings is a dictionary which you can set the maximum allowed concurrent jobs and whether you want to run it in test mode (without actually submitting jobs).
