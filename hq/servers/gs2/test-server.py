import umbridge
import json
import os
import csv
from pyrokinetics import Pyro
import numpy as np
from datetime import datetime
from fileinput import FileInput

batch_size = 900

class GS2Model(umbridge.Model):
    def __init__(self):
        super().__init__("forward")

    def get_input_sizes(self, config):
        return [2 for i in range(batch_size)] 

    def get_output_sizes(self, config):
        return [3 for i in range(batch_size)] 

    def __call__(self, parameters, config):
        # Run the model 
        output = []
        for i in range(batch_size):
            os.system(f"echo {parameters[i][0]} {parameters[i][1]}")
            output.append([parameters[i][0], parameters[i][0], parameters[i][0] + parameters[i][1]])
        return output

    def supports_evaluate(self):
        return True

model = GS2Model()

umbridge.serve_models([model], 4243)
