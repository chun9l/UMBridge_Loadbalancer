#!/bin/bash

#SBATCH -p shared
#SBATCH -J eigen
#SBATCH -N 1
#SBATCH --time=00:01:00
#SBATCH --mem=4G
#SBATCH -n 1


. /home/mghw54/.bashrc
conda activate python3.9

python ../eigen.py ###INPUT###
