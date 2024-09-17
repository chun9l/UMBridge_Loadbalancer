import umbridge
import os
from pyrokinetics import Pyro



class GS2Model(umbridge.Model):
    def __init__(self):
        super().__init__("forward")

    def get_input_sizes(self, config):
        return [1] 

    def get_output_sizes(self, config):
        return [1] 

    def __call__(self, parameters, config):
        iteration = config.get("iteration")
        input_file = "fast.in" # Select input file
        os.chdir("/nobackup/mghw54/gs2test/")
        os.system(f"mkdir -p iteration{iteration}")
        os.chdir(f"iteration{iteration}")
        os.system(f"cp ~/nobackup/gs2dock/usr/gs2/fast.in .")
        pyro = Pyro(gk_file=input_file, gk_code="GS2")
        os.system("mkdir -p restart") # GS2 needs this folder otherwise will fail
        if False: # Added to make it fast! Remove for production runs!
            pyro.gs2_input["knobs"]["nstep"] = 50
            pyro.gs2_input["theta_grid_parameters"]["ntheta"] = 10
            pyro.gs2_input["theta_grid_parameters"]["nperiod"] = 2
            pyro.gs2_input["le_grids_knobs"]["ngauss"] = 5
            pyro.gs2_input["le_grids_knobs"]["negrid"] = 2

        pyro.gs2_input["species_parameters_3"]["tprim"] = float(parameters[0][0])
        pyro.gk_input.data = pyro.gs2_input
        pyro.gk_input.write(input_file)
        
        # Run the model 
        # mpirank = config.get("ranks", 1)
        # os.system(f"sbatch -W /nobackup/mghw54/gs2-batch.sh iteration{iteration}") # --allow-run-as-root to suppress OMPI error, not reccomended when running outside of docker!
        os.system(f"srun --overlap -n64 --mpi=pmix_v3 --nodes=$HQ_NUM_NODES --nodefile=$HQ_NODE_FILE singularity run --bind $TMPDIR ~/nobackup/gs2dock /usr/gs2/bin/gs2 {input_file}")
        # return [[1]] # placeholder
        
        # Read results and print output
        pyro = Pyro(gk_file=input_file, gk_code="GS2")
        pyro.load_gk_output()
        data = pyro.gk_output
        print(data)
        growth_rate = data["growth_rate"].isel(time=-1)
        output = [[growth_rate.to_numpy().squeeze().tolist()]]
        return output 

    def supports_evaluate(self):
        return True

model = GS2Model()
port = int(os.getenv("PORT", 4242))
umbridge.serve_models([model], port)
