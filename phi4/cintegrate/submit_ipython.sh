#!/bin/sh
#SBATCH --job-name ipython
#SBATCH -p test
#SBATCH --nodes 8
#SBATCH --ntasks-per-node 1
#SBATCH --time=00:14:59

## From this man:
## http://twiecki.github.io/blog/2014/02/24/ipython-nb-cluster/

echo "Launching controller"
$HOME/_scratch/anaconda/bin/ipcontroller --ip='*' --ping=100000 &
sleep 10

echo "Launching engines"
srun $HOME/_scratch/anaconda/bin/ipengine &
sleep 25

echo "Launching job"
$HOME/_scratch/anaconda/bin/ipython run_cintegrate.py

echo "Done!"
