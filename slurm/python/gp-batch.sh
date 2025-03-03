#!/bin/bash

#SBATCH -p test
#SBATCH -J gp
#SBATCH -N 1
#SBATCH --time=00:05:00
#SBATCH --mem=4G
#SBATCH -n 1


. /home/mghw54/.bashrc
conda activate python3.9

python gp.py ###INPUT###
