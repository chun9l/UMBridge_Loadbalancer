from batch import batch
from scipy.stats import qmc
import numpy as np
from settings import generate_default_settings
from iteration import iteration
from pyrokinetics import Pyro
import copy
import os

settings = generate_default_settings()

# settings['ncores'] = 64
# settings['cores_per_node'] = 64
settings['max_runs'] = 10
settings['test_mode'] = False

nsample = 100
sampler = qmc.LatinHypercube(d=7, seed=1)
samples = sampler.random(n=100)
samples_scaled = qmc.scale(samples, [0., 0., 2., 0., 0., 0., 0.], [9.0, 0.1, 9., 1., 0.3, 5., 10.])

main_dir = "/nobackup/mghw54/slurm_vs_hq/slurm/gs2-10"
Batch = batch(None, main_dir, settings, sleep_time=0.001)

for i in range(nsample):
    iteration_dir = f"{main_dir}/iteration_{i}/"
    os.system(f"mkdir -p {iteration_dir}")
    os.system(f"cp {main_dir}/../python/gs2-batch.sh {iteration_dir}")
    os.chdir(f"{iteration_dir}")
    os.system(f"mkdir -p {iteration_dir}/restart")
    os.system("cp ~/nobackup/gs2dock/usr/gs2/kbm.in .")
    pyro = Pyro(gk_file="kbm.in", gk_code="GS2")
    pyro.gs2_input["species_parameters_3"]["tprim"] = float(samples_scaled[i][0])
    pyro.gs2_input["species_parameters_3"]["vnewk"] = float(samples_scaled[i][1])
    pyro.gs2_input["theta_grid_parameters"]["qinp"] = float(samples_scaled[i][2])
    pyro.gs2_input["kt_grids_single_parameters"]["aky"] = float(samples_scaled[i][3])
    pyro.gs2_input["parameters"]["beta"] = float(samples_scaled[i][4])
    pyro.gs2_input["theta_grid_eik_knobs"]["s_hat_input"] = float(samples_scaled[i][5])
    pyro.gs2_input["species_parameters_3"]["fprim"] = float(samples_scaled[i][6])
    pyro.gk_input.data = pyro.gs2_input
    pyro.gk_input.write(iteration_dir + "kbm.in")
    Batch.iterations.append(iteration(iteration_dir, settings, batch_file=f"{iteration_dir}/gs2-batch.sh"))



Batch.run()
