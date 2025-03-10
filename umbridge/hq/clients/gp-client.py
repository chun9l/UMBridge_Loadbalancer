import argparse
import umbridge
import numpy as np
import pandas as pd
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from scipy.integrate import fixed_quad
from scipy.special import roots_legendre
import scipy.stats.qmc as qmc
import openturns as ot
import pickle
from sklearn.preprocessing import StandardScaler, MinMaxScaler

class GP:
    def __init__(self, model=None):
        self.model = model
    def fit(self, X, Y):
        input_dim = len(X[0])
        output_dim = len(Y[0])
        constant_basis = ot.ConstantBasisFactory(input_dim).build()
        basis = ot.Basis([ot.AggregatedFunction([constant_basis.build(k) * output_dim]) for k in range(constant_basis.getSize())])
        MaternCov = ot.MaternModel([1.] * input_dim, 1.5)
        covarianceModel = ot.TensorizedCovarianceModel([MaternCov] * output_dim)
        algo = ot.krigingAlgotrithm(X, Y, covarianceModel, basis)
        algo.run()
        self.model = algo.getResult()
    def pred(self, X):
        if self.model is None:
            raise Exception("No GP model")
        else:
            meta = self.model.getMetaModel()
            pred_y = meta(X)
            epsilon = ot.Sample(len(X), [1.0e-8])
            gamma_variance = self.model.getConditionalMarginalVariance(X, 0)
            heat_variance = self.model.getConditionalMarginalVariance(X, 1)
            variance = np.hstack((gamma_variance, heat_variance))
        return np.array(pred_y), np.array(variance)

def integral_function(ky, gamma, Q):
    return ((gamma / np.max(gamma)) / ky ** 2) * Q

def GL_quad(ky, gamma, Q, weight):
    integral = (1 - 0) / 2.0 * np.sum(weight * integral_function(ky, gamma, Q), axis=-1)
    return integral

def call_model(param, workers):
    output_dict = {}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(model, [param[i].tolist()], {"iteration": i}): i for i in range(len(param))}
        for future in as_completed(futures):
            index = futures[future]
            output = future.result()
            output_dict[index] = output
            # print("Done {}".format(i))
    return output_dict

def parabolic_profile(x):
    functions = []
    for i in range(len(x[0])):
        Poly = np.polynomial.Polynomial.fit([0, 1], [min(x[:][i]), max(x[:][i])], 2)
        functions.append(Poly)
    return functions

def remove_variance(x, tol=1e-3):
    nremove = 0
    while np.sqrt(np.mean(x)) > tol:
        x[nremove] = 0
        nremove += 1
    return x, nremove

def GP_integrtation_error(GP, inputs, a, b, n):
    points, w = roots_legendre(n)
    err = ((b - a) ** (2 * n + 1) * math.factorial(n) ** 4) / ((2 * n + 1) * math.factorial(2 * n) ** 3) * GP
    return err

def GL_sum_error(y_f, y_gp, w):
    diff = np.sum((y_f - y_gp) * w)
    return np.abs(diff)

def monte_carlo(ky, gamma, Q):
    return np.mean(integral_function(ky, gamma, Q))

# Read URL from command line argument
parser = argparse.ArgumentParser(description='Minimal HTTP model demo.')
parser.add_argument('url', metavar='url', type=str,
                    help='the URL at which the model is running, for example http://localhost:4242')
args = parser.parse_args()
print(f"Connecting to host URL {args.url}")


# Set up a model by connecting to URL and selecting the "forward" model
model = umbridge.HTTPModel(args.url, "forward")

# print(model.get_input_sizes())
# print(model.get_output_sizes())

with open("matern_gp.pkl", "rb") as h:
    gp = pickle.load(h)
valData = pd.read_csv("ClassifierTargetBatch1.csv")
valData.dropna(inplace=True)

input_df = pd.DataFrame(valData[["ky","q","shat","electron_dens_gradient","beta","electron_nu","electron_temp_gradient"]])
output_df = pd.DataFrame(valData[["growth_rate", "elec_em_flux"]])

standardizer = StandardScaler()
normalizer = MinMaxScaler()

inputs = input_df.values[::10]
outputs = output_df.values[::10]
inputs_scaled = normalizer.fit_transform(np.array(inputs))
outputs_scaled = standardizer.fit_transform(np.array(outputs))

parabolic_functions = parabolic_profile(inputs)
radius = np.linspace(0, 1, 10)
Surrogate = GP(gp)

nsample = 2000
sampler = qmc.LatinHypercube(d=1, seed=1)
sample = sampler.random(n=nsample)
samples = qmc.scale(sample, [0.0], [1.0])

tol = 5e-2

integral = []
surrogate_error = []
for i in radius:
    input_params = []
    # sample_points, weights = roots_legendre(order)
    # ky = (1 - 0) * (sample_points + 1) / 2.0 + 0
    for j in range(len(samples)):
        non_ky = [parabolic_functions[k](i) for k in range(1, 7)]
        non_ky.insert(0, samples[j][0])
        input_params.append(non_ky)
    input_params = normalizer.transform(np.array(input_params))
    pred, var = Surrogate.pred(input_params)
    pred = standardizer.inverse_transform(pred)
    var = standardizer.inverse_transform(var) * standardizer.var_
    sample_var = np.var(pred, axis=0, ddof=1)
    MC_error = np.sqrt(np.sum(sample_var)) / np.sqrt(nsample)
    err_tol = min(MC_error, tol)
    if np.sqrt(np.mean(var)) > 1:
        sort_index = np.argsort(np.sum(var, axis=-1))[::-1]
        var = var[sort_index]
        input_params = input_params[sort_index]
        var_reduced, nremoved = remove_variance(var, err_tol)
        input_params_reduced = input_params[: -nremoved]
        pred_reduced = pred[: -nremoved]
        eval_points = normalizer.inverse_transform(input_params[-nremoved:])
        output_dict = call_model(eval_points, 2)
        sim_outputs = np.array([output_dict[i][0] for i in range(nremoved)])
        # inputs_scaled = np.append(inputs_scaled, eval_points, axis=0)
        # outputs_scaled = np.append(outputs_scaled, sim_outputs, axis=0)
        pred_new = np.append(pred_reduced, sim_outputs, axis=0)
        integral.append(monte_carlo(samples, pred_new[:, 0], pred_new[:, 1]))
        surrogate_error.append(np.sqrt(np.mean(var_reduced)))
    else:
        integral.append(monte_carlo(samples, pred[:, 0], pred[:, 1]))
        surrogate_error.append(np.sqrt(np.mean(var)))
    print("Done radius {}".format(i))

print(integral)
print(surrogate_error)

        



# Simple model evaluation without config
"""
valData = pd.read_csv("../validationData.csv")
targets = pd.DataFrame(valData[["ky", "q", "shat", "electron_dens_gradient", "beta", "electron_nu", "electron_temp_gradient"]])
param = targets.to_numpy()[:100, :]

mod = jit.load("gp_model.pt")
"""


"""
for i in range(len(param)):
    config={"iteration": i}
    print(param[i].tolist())
    print(model([param[i].tolist()], config))
"""

