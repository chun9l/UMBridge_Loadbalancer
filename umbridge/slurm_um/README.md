# HPC
This folder cotains the code for the SLURM backend part of the experiments. You will need the UM-Bridge package for Python which can be easily install with `pip install umbridge`. The load balancer is written in C++. We provide a Makefile to compile it with GNU, please modify it if you have a different compiler. 

## Usage

The load balancer is primarily intended to run on a login node.

1. **Configure resource allocation**

   The load balancer will submit the script ``hpc/slurm_scripts/job.sh`` to SLURM via `sbatch`. Adapt the `#SBATCH` configuration in this file to your needs.

2. **Configure model job**

   In the same `job.sh` file, you can specify what UM-Bridge model server to run,
   Importantly, the UM-Bridge model server must serve its models at the port specified by the environment variable `PORT`. The value of `PORT` is automatically determined by `job.sh`, avoiding potential conflicts if multiple servers run on the same compute node.

   **Timing logs**
   
   We obtain job metadata using the SLURM job IDs which we will extract from the SLURM outputs. We recommend creating a designated directory to store these, e.g., `2jobs/gs2/`. Modify the `#SBATCH -o` and `#SBATCH -e` directives to pipe the stdout/err into the designated directory.

4. **Run load balancer**

   Navigate to the `hpc` directory and execute the load balancer.

   ```
   ./load-balancer --scheduler=slurm --port=<port>
   ```

5. **Connect from client**

   Once running, you can connect to the load balancer from any UM-Bridge client on the login node via `http://localhost:<port>`. You can control how many concurrent jobs allowed using the `max_worker` parameter in the Python client.

   **Extract job timings**

   The content of the SLURM output is not useful in this paper; we only want the Job ID. Run the `job-time-slurm.py` script to extract the timings. You will need to modify the Python script with an appropriate file path.

   **Plotting**
   We provide Python scripts to plot the times extracted in the previous step.
