import torch 
from torch import jit
import argparse

def GP(inputs):
    mod = jit.load("../gr_traced_7d.pt")
    mod2 = jit.load("../freq_traced_7d.pt")
    mean, std = mod(inputs)
    mean2, std2 = mod2(inputs)
    return 

parser = argparse.ArgumentParser(description="Give the list of inputs")
parser.add_argument("inputs", type=float, nargs="*")
args = parser.parse_args()


inputs = torch.tensor([args.inputs])

GP(inputs)
