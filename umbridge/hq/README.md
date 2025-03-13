# HPC
This folder cotains the code for the HyperQueue part of the experiments. You will need the UM-Bridge package for Python which can be easily install with `pip install umbridge`. The load balancer is written in C++. We provide a Makefile to compile it with GNU, please modify it if you have a different compiler. HyperQueue is bundled in the repo for ease of access.


## Usage

The load balancer is primarily intended to run on a login node.

1. **Configure resource allocation**

   The load balancer instructs HyperQueue to allocate batches of resources on the HPC system, depending on demand for model evaluations. HyperQueue will submit SLURM or PBS jobs on the HPC system when needed, scheduling requested model runs within those jobs. When demand decreases, HyperQueue will cancel some of those jobs again.

   Adapt the configuration in ``hpc/hq_scripts/allocation_queue.sh`` to your needs. You can find the configurable options in the HyperQueue documentation.

2. **Configure model job**

   Adapt the configuration in ``hpc/hq_scripts/job.sh`` to your needs:
   * Specify what UM-Bridge model server to run,
   * and set `#HQ` variables at the top to specify what resources each instance should receive.

   Importantly, the UM-Bridge model server must serve its models at the port specified by the environment variable `PORT`. The value of `PORT` is automatically determined by `job.sh`, avoiding potential conflicts if multiple servers run on the same compute node.

   **Timing logs**
   
   HQ provides a flag to record job metadata. This needs to be modified in the LoadBalancer.cpp file at the line with `./hq server start --journal=<log_name>`. Remember to recompile after changing this.

4. **Run load balancer**

   Navigate to the `hpc` directory and execute the load balancer.

   ```
   ./load-balancer --scheduler=hyperqueue --port=<port>
   ```

5. **Connect from client**

   Once running, you can connect to the load balancer from any UM-Bridge client on the login node via `http://localhost:<port>`. The `max_workers` parameter in the client needs to match the number of parallel servers running. 

   **Extract job timings**

   HQ will generate many job folders to hold the job outputs, but they are not useful for the purpose of this work. The job logs stored in `<log_name>` needs some postprocessing. This can be done by running `./hq event-log export <log_name> > <processed_log>`, and follow by `job-time-hq.py`. You need to modify the latter Python script with an appropriate file path.

   **Plotting**
   We provide Python scripts to plot the times extracted in the previous step.
