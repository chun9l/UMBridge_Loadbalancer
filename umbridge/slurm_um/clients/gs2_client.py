import argparse
import umbridge
import numpy as np
from scipy.stats import qmc
from concurrent.futures import ThreadPoolExecutor, as_completed

# Read URL from command line argument
parser = argparse.ArgumentParser(description='Minimal HTTP model demo.')
parser.add_argument('url', metavar='url', type=str,
                    help='the URL at which the model is running, for example http://localhost:4242')
args = parser.parse_args()
print(f"Connecting to host URL {args.url}")

# Print modelssupported by server
# print(umbridge.supported_models(args.url))

# Set up a model by connecting to URL and selecting the "forward" model
model = umbridge.HTTPModel(args.url, "forward")

# print(model.get_input_sizes())
# print(model.get_output_sizes())


# Simple model evaluation without config
sampler = qmc.LatinHypercube(d=7, seed=1)
sample = sampler.random(n=100)
param = qmc.scale(sample, [0.0, 0.0, 2.0, 0.0, 0., 0., 0.], [9., 0.1, 9., 1., 0.3, 5., 10.]) # tprim, vnewk, qinp, aky, beta, shat, fprim

with ThreadPoolExecutor(max_workers=2) as executor:
    futures = {executor.submit(model, [param[i].tolist()], {"iteration": i}): i for i in range(len(param))}
    i = 0
    for future in as_completed(futures):
        input = param[futures[future]]
        print(input)
        print(future.result())
        print("Done {}".format(futures[future]))
        i += 1

"""
for i in range(len(param)):
    config={"iteration": i}
    print(param[i].tolist())
    print(model([param[i].tolist()], config))
"""
