#!/bin/sh
#SBATCH --job-name ipython
#SBATCH -p regular6
#SBATCH --nodes 19
#SBATCH --time=23:14:58

## From this man:
## http://twiecki.github.io/blog/2014/02/24/ipython-nb-cluster/

echo "Launching controller"
$HOME/_scratch/anaconda/bin/ipcontroller --ip='*' --ping=100000 &
sleep 10

echo "Launching engines"
srun  $HOME/_scratch/anaconda/bin/ipengine &
sleep 25

echo "Launching job"
time $HOME/_scratch/anaconda/bin/ipython run_cintegrate.py $1

echo "Done!"
