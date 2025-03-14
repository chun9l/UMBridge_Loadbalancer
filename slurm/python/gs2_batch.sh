#!/bin/bash

#SBATCH -p shared
#SBATCH -J gs2
#SBATCH -N 1
#SBATCH --time=4:00:00
#SBATCH --mem=32G
#SBATCH -n 8


. /home/mghw54/.bashrc
conda activate python3.9
module load gcc openmpi

mpirun singularity run --bind=$TMPDIR ~/nobackup/gs2dock/ /usr/gs2/bin/gs2 kbm.in
