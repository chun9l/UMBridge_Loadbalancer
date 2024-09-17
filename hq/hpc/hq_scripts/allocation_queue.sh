#! /bin/bash

# Note: For runs on systems without SLURM, replace the slurm allocator by
# hq worker start &


./hq alloc add slurm --time-limit=00:05:00 \
                   --backlog 1 \
                   --workers-per-alloc 2 \
                   --max-worker-count 2 \
                   -- -p shared --mem=1G --ntasks-per-node=1 # Add any neccessary SLURM arguments
# Any parameters after -- will be passed directly to sbatch (e.g. credentials, partition, mem, etc.)
