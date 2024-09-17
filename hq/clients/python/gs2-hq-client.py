#!/usr/bin/env python3
import argparse
import umbridge
import numpy as np
from scipy.stats import qmc

# Read URL from command line argument
parser = argparse.ArgumentParser(description='Minimal HTTP model demo.')
parser.add_argument('url', metavar='url', type=str,
                    help='the URL at which the model is running, for example http://localhost:4242')
args = parser.parse_args()
print(f"Connecting to host URL {args.url}")

# Print modelssupported by server
print(umbridge.supported_models(args.url))

# Set up a model by connecting to URL and selecting the "forward" model
model = umbridge.HTTPModel(args.url, "forward")

print(model.get_input_sizes())
print(model.get_output_sizes())


# Simple model evaluation without config
sampler = qmc.LatinHypercube(d=7, seed=1)
sample = sampler.random(n=500)
param = qmc.scale(sample, [0.5, 0.0, 2.0, 0.04, 0.0, 0.0, 0.0], [6.0, 0.1, 9.0, 1.0, 0.3, 5.0, 10.0])[127: 281] # tprim, vnewk, q, ky, beta, shat, fprim
for i in range(len(param)):
    config={"iteration": i + 282}
    print(param[i].tolist())
    print(model([param[i].tolist()], config))


# Model evaluation with configuration parameters
config={"vtk_output": True, "level": 1}
#print(model(param, config))

# If model supports Jacobian action,
# apply Jacobian of output zero with respect to input zero to a vector
if model.supports_apply_jacobian():
  print(model.apply_jacobian(0, 0, param, [1.0, 4.0]))
