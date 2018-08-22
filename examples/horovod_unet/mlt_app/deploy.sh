#! /bin/bash
# Copyright (c) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: EPL-2.0
#

# install ksonnet + kubeflow openmpi so we can support Horovod distributed training

VERSION=master
SECRET=openmpi-secret
# https://github.com/ksonnet/ksonnet/issues/298
export USER=root

# set your GITHUB_TOKEN otherwise deployment will fail with API Limit error
export GITHUB_TOKEN=$GITHUB_TOKEN

# Please update physical cores value. Below command works for linux.
#export PHYSICAL_CORES=`lscpu | grep "Core(s) per socket" | cut -d':' -f2 | sed "s/ //g"` # Total number of physical cores per socket
export PHYSICAL_CORES=4

{
# Generate one-time ssh keys used by Open MPI.
SECRET=openmpi-secret
mkdir -p .tmp
yes 2>/dev/null | ssh-keygen -N "" -f .tmp/id_rsa
kubectl delete secret ${SECRET} -n ${NAMESPACE} || true
kubectl create secret generic ${SECRET} -n ${NAMESPACE} --from-file=id_rsa=.tmp/id_rsa --from-file=id_rsa.pub=.tmp/id_rsa.pub --from-file=authorized_keys=.tmp/id_rsa.pub
rm -rf .tmp

# Initialize a ksonnet app. Set the namespace for it's default environment.
if [ -d "$JOB_NAME" ]; then
  pushd .
  cd ${JOB_NAME}
  set +e
  ks delete default
  ks component rm ${JOB_NAME}
  set -e
  popd
  rm -rf ${JOB_NAME}
fi

ks init ${JOB_NAME}
cd ${JOB_NAME}
ks env set default --namespace ${NAMESPACE}

# Install openmpi kubeflow component.
ks registry add kubeflow github.com/kubeflow/kubeflow/tree/${VERSION}/kubeflow
ks pkg install kubeflow/openmpi@${VERSION}

# Temporary fix for volume-mount
# Untill this is merged : https://github.com/kubeflow/kubeflow/issues/838
cp -rf ../volume-mount/workloads.libsonnet vendor/kubeflow/openmpi/
cp -rf ../volume-mount/prototypes/openmpi.jsonnet vendor/kubeflow/openmpi/prototypes/

# Generate openmpi components.

# Node selector helps to launch job on specific set of nodes with label.
# For kubernetes nodes we assigned label called `node-type=highmem` to set of nodes.
# Ex: kubectl label node gke-node-1 node-type=highmem
NODE_SELECTOR="node-type=highmem"

COMPONENT=${JOB_NAME}

# data path for training data
DATA_PATH=${DATA_PATH}

# output path to store results
OUTPUT_PATH=${OUTPUT_PATH}

IMAGE=${IMAGE}
WORKERS=$(( ${NUM_NODES} * ${NUM_WORKERS_PER_NODE} ))
SOCKETS_PER_NODE=${SOCKETS_PER_NODE}
NUM_INTER_THREADS=${NUM_INTER_THREADS}

PPR=$(( $NUM_WORKERS_PER_NODE / $SOCKETS_PER_NODE ))
PE=$(( $PHYSICAL_CORES / $PPR ))

GPU=${GPUS}
EXEC="mpirun -np ${WORKERS} \
--hostfile /kubeflow/openmpi/assets/hostfile \
--map-by socket \
-cpus-per-proc $PHYSICAL_CORES \
--report-bindings \
--oversubscribe bash /src/app/exec_multiworker.sh ${PPR} ${NUM_INTER_THREADS} ${DATA_PATH} ${OUTPUT_PATH}"

ks generate openmpi ${COMPONENT} --image ${IMAGE} --secret ${SECRET} --workers ${WORKERS} --gpu ${GPU} --exec "${EXEC}" --nodeSelector "${NODE_SELECTOR}"
} &> /dev/null

# Uncomment below params to mount data.

# If you have data on your host, if you want to mount that as volume. Please update below paths
# volumes - path in this section will create a volume for you based on host path provided
# volumeMounts - mountPath in this section will mount above volume at specified location
ks param set ${COMPONENT} volumes '[{ "name": "vol", "hostPath": { "path": "/var/datasets/unet/vck-resource-8fd827a8-809a-11e8-b982-0a580a480bd4" }}]'
ks param set ${COMPONENT} volumeMounts '[{ "name": "vol", "mountPath": "/var/datasets/unet/vck-resource-8fd827a8-809a-11e8-b982-0a580a480bd4"}]'

# Deploy to your cluster.
ks apply default
