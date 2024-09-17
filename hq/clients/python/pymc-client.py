import argparse
import numpy as np
import pymc as pm
from pytensor import tensor as pt
from pytensor.gradient import verify_grad
import arviz as az
import matplotlib.pyplot as plt
from umbridge.pymc import UmbridgeOp


if __name__ == "__main__":
    # Read URL from command line argument
    parser = argparse.ArgumentParser(description='Minimal HTTP model demo.')
    parser.add_argument('url', metavar='url', type=str,
                        help='the URL at which the model is running, for example http://localhost:4242')
    args = parser.parse_args()
    print(f"Connecting to host URL {args.url}")

    # Set up an pytensor op connecting to UM-Bridge model
    op = UmbridgeOp(args.url, "posterior")

    # Define input parameter
    input_dim = 2
    input_val = [0.0, 10.0]

    # Evaluate model with input parameter
    op_application = op(pt.as_tensor_variable(input_val))
    print(f"Model output: {op_application.eval()}")

    # Verify gradient
    print("Check model's gradient against numerical gradient. This requires an UM-Bridge model with gradient support.")
    verify_grad(op, [input_val], rng = np.random.default_rng())

    with pm.Model() as model:
        # UM-Bridge models with a single 1D output implementing a PDF
        # may be used as a PyMC density that in turn may be sampled
        posterior = pm.DensityDist('posterior',logp=op,shape=input_dim)

        map_estimate = pm.find_MAP()
        print(f"MAP estimate of posterior is {map_estimate['posterior']}")

        inferencedata = pm.sample(tune=100,draws=400,cores=1)
        az.plot_pair(inferencedata);
        plt.show()
