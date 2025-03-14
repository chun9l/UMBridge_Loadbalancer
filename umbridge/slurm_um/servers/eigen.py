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
        if dimension == None:
            raise Exception("Input a dimension for the square matrix")
        np.random.seed(1)

        iteration = config.get("iteration")

        main_dir = "/nobackup/mghw54/slurm_vs_hq/umbridge/slurm_um"
        iter_dir = main_dir + os.sep + f"eigen_{int(dimension[0][0])}" + os.sep + f"iteration{iteration}"
        os.system(f"mkdir -p {iter_dir}")

        # Dimension for the matrix used in eigenvalue calculation    
        matrix = np.random.rand(int(dimension[0][0]), int(dimension[0][0]))
        eigenvalues, _ = np.linalg.eig(matrix)  # computationally expensive eigenvalue calculation  
        print("Done")
        return [[1]] # Placeholder since we are not interested in the outcome 

    def supports_evaluate(self):
        return True


model = Eigen()
port = int(os.getenv("PORT", 4242))
umbridge.serve_models([model], port)
