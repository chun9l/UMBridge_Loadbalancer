#! /bin/bash

# Note: For runs on systems without SLURM, replace the slurm allocator by
# hq worker start &


./hq alloc add slurm --time-limit=00:10:00 \
                   --backlog 1 \
                   --workers-per-alloc 10 \
                   --max-worker-count 10 \
                   -- -p shared --exclude=cn[079,005,003,101,020,100,053,059,086,030,051,035,070,090] --mem=4G --ntasks-per-node=1 # Add any neccessary SLURM arguments
# Any parameters after -- will be passed directly to sbatch (e.g. credentials, partition, mem, etc.)
