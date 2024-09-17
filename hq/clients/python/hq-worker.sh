#!/bin/bash
#SBATCH --nodes=2
#SBATCH --time=00:15:00
#SBATCH -p shared
#SBATCH --ntasks-per-node=3
#SBATCH -o out.txt
#SBATCH -e err.txt

module load gcc openmpi 

srun -N1 -n 1 --overlap /home/mghw54/hq worker start --idle-timeout "5m" --manager "slurm" --server-dir "/home/mghw54/.hq-server/283" --on-server-lost "finish-running" --time-limit "15m" &
srun -N1 -n 1 --overlap /home/mghw54/hq worker start --idle-timeout "5m" --manager "slurm" --server-dir "/home/mghw54/.hq-server/283" --on-server-lost "finish-running" --time-limit "15m" &
wait
