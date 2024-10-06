#! /bin/bash

# Note: For runs on systems without SLURM, replace the slurm allocator by
# hq worker start &


./hq alloc add slurm --time-limit=00:10:00 \
                   --backlog 1 \
                   --workers-per-alloc 1 \
                   --max-worker-count 1 \
                   -- -p shared --mem=4G -w cn085 --ntasks-per-node=1 # Add any neccessary SLURM arguments
# Any parameters after -- will be passed directly to sbatch (e.g. credentials, partition, mem, etc.)
