import argparse
import umbridge
import numpy as np
import pandas as pd
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
valData = pd.read_csv("../validationData.csv")
targets = pd.DataFrame(valData[["ky", "q", "shat", "electron_dens_gradient", "beta", "electron_nu", "electron_temp_gradient"]])
param = targets.to_numpy()[:100, :]

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(model, [param[i].tolist()]): i for i in range(len(param))}
    i = 0
    for future in as_completed(futures):
        input = param[futures[future]]
        print(input)
        print(future.result())
        print("Done {}".format(i))
        i += 1

"""
for i in range(len(param)):
    config={"iteration": i}
    print(param[i].tolist())
    print(model([param[i].tolist()], config))
"""

