import os
import time
import umbridge
import numpy as np

# Inspired by https://github.com/chi-feng/mcmc-demo

class Donut(umbridge.Model):
    def __init__(self):
        super().__init__("posterior")


    def get_input_sizes(self, config):
        return [1]

    def get_output_sizes(self, config):
        return [1]

    def __call__(self, dimension, config):

        # miscallaneous additional maths to make job more cpu intensive
        # will better display scheduler and load balancer ability,
        # as very low times are bottlenecked by the client itself

        if dimension == None:
            raise Exception("Input a dimension for the square matrix")
        np.random.seed(1)

        # Dimension for the matrix used in eigenvalue calculation    
        matrix = np.random.rand(int(dimension[0][0]), int(dimension[0][0]))
        eigenvalues, _ = np.linalg.eig(matrix)  # computationally expensive eigenvalue calculation  
        print("Done")
        return [[1]] # Placeholder

    def supports_evaluate(self):
        return True

    def gradient(self, out_wrt, in_wrt, parameters, sens, config):
        r = np.linalg.norm(parameters[0])
        if (r == 0):
            return [0,0]
        return [sens[0] * parameters[0][0] * (Donut.radius / r - 1) * 2 / Donut.sigma2,
                sens[0] * parameters[0][1] * (Donut.radius / r - 1) * 2 / Donut.sigma2]

    def supports_gradient(self):
        return False

    def apply_jacobian(self, out_wrt, in_wrt, parameters, vec, config):
        r = np.linalg.norm(parameters[0])
        if (r == 0):
            return [0]
        return [vec[0] * parameters[0][0] * (Donut.radius / r - 1) * 2 / Donut.sigma2
              + vec[1] * parameters[0][1] * (Donut.radius / r - 1) * 2 / Donut.sigma2]

    def supports_apply_jacobian(self):
        return False

model = Donut()
port = int(os.getenv("PORT", 4242))
umbridge.serve_models([model], port)
