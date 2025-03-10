import os
import umbridge
import numpy as np

class Eigen(umbridge.Model):
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


model = Eigen()
port = int(os.getenv("PORT", 4242))
umbridge.serve_models([model], port)
