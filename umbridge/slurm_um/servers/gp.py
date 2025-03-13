import torch
import os
from torch import jit
import umbridge
 

class GPModel(umbridge.Model):
    def __init__(self):
        super().__init__("forward")

    def get_input_sizes(self, config):
        return [7]
    
    def get_output_sizes(self, config):
        return [2]

    def __call__(self, inputs, config):
        mod = jit.load("../gr_traced_7d.pt")
        mod2 = jit.load("../freq_traced_7d.pt")
#Create a torch tensor with appropriate values
        inputs = torch.tensor(inputs)

        mean,std = mod(inputs)
        mean2,std2 = mod2(inputs)
        return [torch.cat((mean, mean2)).tolist()]

    def supports_evaluate(self):
        return True

model = GPModel()
port = int(os.getenv("PORT", 4242))
umbridge.serve_models([model], port)

