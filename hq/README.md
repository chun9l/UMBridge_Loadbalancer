# HPC
This folder cotains the code for the HyperQueue part of the experiments. You will need the UM-Bridge package for Python which can be easily install with `pip install umbridge`. The load balancer is written in C++. We provide a Makefile to compile it with GNU, please modify it if you have a different compiler. HyperQueue is bundled in the repo for ease of access.


## Usage

The load balancer is primarily intended to run on a login node.

1. **Configure resource allocation**

   The load balancer instructs HyperQueue to allocate batches of resources on the HPC system, depending on demand for model evaluations. HyperQueue will submit SLURM or PBS jobs on the HPC system when needed, scheduling requested model runs within those jobs. When demand decreases, HyperQueue will cancel some of those jobs again.

   Adapt the configuration in ``hpc/hq_scripts/allocation_queue.sh`` to your needs. You can find the configurable options in the HyperQueue documentation.

   For example, when running a very fast UM-Bridge model on an HPC cluster, it is advisable to choose medium-sized jobs for resource allocation. That will avoid submitting large numbers of jobs to the HPC system's scheduler, while HyperQueue itself will handle large numbers of small model runs within those allocated jobs.

2. **Configure model job**

   Adapt the configuration in ``hpc/hq_scripts/job.sh`` to your needs:
   * Specify what UM-Bridge model server to run,
   * and set `#HQ` variables at the top to specify what resources each instance should receive.

   Importantly, the UM-Bridge model server must serve its models at the port specified by the environment variable `PORT`. The value of `PORT` is automatically determined by `job.sh`, avoiding potential conflicts if multiple servers run on the same compute node.

4. **Run load balancer**

   Navigate to the `hpc` directory and execute the load balancer.

   ```
   ./load-balancer
   ```

5. **Connect from client**

   Once running, you can connect to the load balancer from any UM-Bridge client on the login node via `http://localhost:4242`. To the client, it will appear like any other UM-Bridge server, except that it can process concurrent evaluation requests.
