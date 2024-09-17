from batch import batch
from scipy.stats import qmc
import numpy as np
from settings import generate_default_settings
from iteration import iteration
from pyrokinetics import Pyro
import copy
import os

settings = generate_default_settings()

settings['ncores'] = 64
settings['cores_per_node'] = 64
settings['max_runs'] = 2
settings['check_tearing'] = False
settings['check_apar_phi_ratio'] = False
settings['check_end_line_amp'] = False
settings['check_apar_phi_integral_ratio'] = False
settings['check_frequency_sign'] = False
settings['test_mode'] = False
settings['use_containers'] = False
settings['image'] = "gs2dock"

nsample = 100
sampler = qmc.LatinHypercube(d=1, seed=1)
samples = sampler.random(n=100)
samples_scaled = qmc.scale(samples, [0.], [9.0])

main_dir = "/nobackup/mghw54/gs2test-slurm"
Batch = batch(None, main_dir, settings)

for i in range(nsample):
    iteration_dir = f"{main_dir}/iteration_{i}/"
    os.system(f"mkdir -p {iteration_dir}/restart")
    pyro = Pyro(gk_file="fast.in", gk_code="GS2")
    pyro.gs2_input["species_parameters_3"]["tprim"] = samples_scaled[i]
    pyro.gk_input.data = pyro.gs2_input
    pyro.gk_input.write(iteration_dir + "gs2.in")
    Batch.iterations.append(iteration(iteration_dir, settings))



Batch.run()
