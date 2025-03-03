import numpy as np
import argparse

parser = argparse.ArgumentParser(description="Sets the dimension of square matrix")
parser.add_argument("dimension", metavar="dimension", type=str)
args = parser.parse_args()


def eigen(seed, dimension):
    np.random.seed(seed)
    A = np.random.rand(dimension, dimension)
    np.linalg.eig(A)
    return

if args.dimension:
    eigen(1, int(args.dimension))
else:
    raise Exception("Dimension not set")
