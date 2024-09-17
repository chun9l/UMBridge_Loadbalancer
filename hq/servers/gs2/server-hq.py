import umbridge
import json
import os
import csv
from pyrokinetics import Pyro
import numpy as np
from datetime import datetime
from fileinput import FileInput


class GS2Model(umbridge.Model):
    def __init__(self):
        super().__init__("forward")

    def get_input_sizes(self, config):
        return [2] 

    def get_output_sizes(self, config):
        return [3] 

    def __call__(self, parameters, config):
        input_file = "/home/mghw54/gs2dock/hq-test/fast.in" # Select input file
        dt = str(datetime.now()) # Creates timestamp unique to each run
        dt = dt.split(" ")[0] + "_" + dt.split(" ")[1].replace(":", "-")
        print("Code running in server")
        with FileInput(files=input_file, inplace=True) as file:
            checkpoint = 0
            for line in file:
                if "&species_parameters_3" in line:
                    checkpoint += 1
                if "tprim" in line and checkpoint == 1:
                    line = f"    tprim = {parameters[0][0]}"
                if "vnewk" in line and checkpoint == 1:
                    line = f"    vnewk = {parameters[0][1]}"
                print(line.rstrip()) # FileInput redirects stdout to file
        
        # Run the model 
        os.system(f"cd ~/gs2dock/hq-test && mpirun -ppn 2 -np 2 singularity run ~/gs2dock /usr/gs2/bin/gs2 {input_file} ; echo $?")

        
        # Read results using Pyrokinetics package and print output
        pyro = Pyro(gk_file=input_file, gk_code="GS2")
        pyro.load_gk_output()
        data = pyro.gk_output
        heat = data["heat"].sel(species="electron", field='phi').isel(time=-1)
        growth_rate = data["growth_rate"].isel(time=-1)
        mode_freq = data["mode_frequency"].isel(time=-1)
        output = [[heat.to_numpy().squeeze().tolist(), growth_rate.to_numpy().squeeze().tolist(), mode_freq.to_numpy().squeeze().tolist()]]
        return output 

    def supports_evaluate(self):
        return True

port = 0
if "PORT" in os.environ:
    port = os.environ['PORT']
else:
    port = 4242

model = GS2Model()
umbridge.serve_models([model], int(port))
