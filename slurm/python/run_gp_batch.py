from batch import batch
from settings import generate_default_settings
from iteration import iteration
import copy
import pandas as pd
import os

settings = generate_default_settings()

settings['ncores'] = 1
settings['cores_per_node'] = 1
settings['max_runs'] = 10
settings['test_mode'] = False

nsample = 100

main_dir = f"/nobackup/mghw54/slurm_vs_hq/slurm/{settings['max_runs']}jobs/gp"
Batch = batch(None, main_dir, settings, sleep_time=0.0005)

valData = pd.read_csv("validationData.csv")
targets = pd.DataFrame(valData[["ky", "q", "shat", "electron_dens_gradient", "beta", "electron_nu", "electron_temp_gradient"]])
param = targets.to_numpy()[:nsample, :]

for i in range(nsample):
    iteration_dir = f"{main_dir}/iteration_{i}"
    os.system(f"mkdir -p {iteration_dir}")
    os.system(f"cp gp-batch.sh {iteration_dir}")
    os.system(f"cp gp.py {iteration_dir}")
    with open(f"{iteration_dir}/gp-batch.sh", "r") as h:
        filedata = h.read()
    
    input_str = " ".join(str(i) for i in list(param[i]))
    filedata = filedata.replace("###INPUT###", input_str)

    with open(f"{iteration_dir}/gp-batch.sh", "w") as h:
        h.write(filedata)

    Batch.iterations.append(iteration(iteration_dir, settings, batch_file=f"{iteration_dir}/gp-batch.sh"))



Batch.run()
