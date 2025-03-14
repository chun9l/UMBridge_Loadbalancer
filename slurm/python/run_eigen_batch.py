from batch import batch
import numpy as np
from settings import generate_default_settings
from iteration import iteration
import copy
import os

settings = generate_default_settings()

settings['max_runs'] = 50
settings['test_mode'] = False

nsample = 100
dimension = 5000

main_dir = f"/nobackup/mghw54/slurm_vs_hq/slurm/{settings['max_runs']}jobs/eigen_{dimension}"
Batch = batch(None, main_dir, settings, sleep_time=0.0005)

os.system(f"cp eigen_batch.sh {main_dir}")
os.system(f"cp eigen.py {main_dir}")

with open(f"{main_dir}/eigen_batch.sh", "r") as h:
    filedata = h.read()

filedata = filedata.replace("###INPUT###", str(dimension))

with open(f"{main_dir}/eigen_batch.sh", "w") as h:
    h.write(filedata)

for i in range(nsample):
    iteration_dir = f"{main_dir}/iteration_{i}"
    os.system(f"mkdir -p {iteration_dir}")
    Batch.iterations.append(iteration(iteration_dir, settings, batch_file=f"{main_dir}/eigen_batch.sh"))



Batch.run()
