import umbridge
import os
from pyrokinetics import Pyro



class GS2Model(umbridge.Model):
    def __init__(self):
        super().__init__("forward")

    def get_input_sizes(self, config):
        return [7] 

    def get_output_sizes(self, config):
        return [2] 

    def __call__(self, parameters, config):
        iteration = config.get("iteration")
        input_file = "kbm.in" # Select input file
        os.chdir("/nobackup/mghw54/slurm_vs_hq/umbridge/slurm_um/10jobs/gs2")
        os.system(f"mkdir -p iteration{iteration}")
        os.chdir(f"iteration{iteration}")
        os.system(f"cp ~/nobackup/gs2dock/usr/gs2/kbm.in .")
        pyro = Pyro(gk_file=input_file, gk_code="GS2")
        os.system("mkdir -p restart") # GS2 needs this folder otherwise will fail

        pyro.gs2_input["species_parameters_3"]["tprim"] = float(parameters[0][6])
        pyro.gs2_input["species_parameters_3"]["vnewk"] = float(parameters[0][5])
        pyro.gs2_input["theta_grid_parameters"]["qinp"] = float(parameters[0][1])
        pyro.gs2_input["kt_grids_single_parameters"]["aky"] = float(parameters[0][0])
        pyro.gs2_input["parameters"]["beta"] = float(parameters[0][4])
        pyro.gs2_input["theta_grid_eik_knobs"]["s_hat_input"] = float(parameters[0][2])
        pyro.gs2_input["species_parameters_3"]["fprim"] = float(parameters[0][3])
        pyro.gk_input.data = pyro.gs2_input
        pyro.gk_input.write(input_file)
        
        # Run the model 
        # mpirank = config.get("ranks", 1)
        # os.system(f"sbatch -W /nobackup/mghw54/gs2dock/usr/gs2/gs2-batch.sh iteration{iteration}") # --allow-run-as-root to suppress OMPI error, not reccomended when running outside of docker!
        os.system(f"mpirun -n 8 singularity run --bind $TMPDIR ~/nobackup/gs2dock /usr/gs2/bin/gs2 {input_file}")
        
        # Read results and print output
        pyro = Pyro(gk_file=input_file, gk_code="GS2")
        pyro.load_gk_output()
        data = pyro.gk_output
        heat = data["heat"].sel(species="electron", field='phi').isel(time=-1)
        growth_rate = data["growth_rate"].isel(time=-1)
        # mode_freq = data["mode_frequency"].isel(time=-1)
        output = [[growth_rate.to_numpy().squeeze().tolist(), heat.to_numpy().squeeze().tolist()]]
        return [[1, 1]] # Placeholder since we don't care 

    def supports_evaluate(self):
        return True

model = GS2Model()
port = int(os.getenv("PORT", 4242))
umbridge.serve_models([model], port)
