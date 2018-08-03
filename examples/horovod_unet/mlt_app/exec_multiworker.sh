#! /bin/bash

# Execute training on each node, pulling local thread counts for the train script
cd /src/app

export physical_cores=`lscpu | grep "Core(s) per socket" | cut -d':' -f2 | sed "s/ //g"` # Total number of physical cores per socket
export num_threads=$(( ${2} * $physical_cores )) # Total number of physical cores on this machine

python hvd_train.py --logdir="tensorboard${1}" --num_inter_threads=${3} --num_threads=$num_threads
