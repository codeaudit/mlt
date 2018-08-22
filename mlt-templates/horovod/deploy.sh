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

{
# Generate one-time ssh keys used by Open MPI.
SECRET=openmpi-secret
mkdir -p .tmp
echo "y" | ssh-keygen -N "" -f .tmp/id_rsa
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

# Temporary fix for volume-mount.
# Untill this is merged : https://github.com/kubeflow/kubeflow/issues/838
cp -rf ../volume-mount/workloads.libsonnet vendor/kubeflow/openmpi/
cp -rf ../volume-mount/prototypes/openmpi.jsonnet vendor/kubeflow/openmpi/prototypes/

# Generate openmpi components.
COMPONENT=${JOB_NAME}
IMAGE=${IMAGE}
WORKERS=${NUM_WORKERS}
GPU=${GPUS}
EXEC="mpiexec -n ${WORKERS} --hostfile /kubeflow/openmpi/assets/hostfile --allow-run-as-root --display-map --tag-output --timestamp-output sh -c 'python /src/app/main.py'"
ks generate openmpi ${COMPONENT} --image ${IMAGE} --secret ${SECRET} --workers ${WORKERS} --gpu ${GPU} --exec "${EXEC}"

} &> /dev/null

# Uncomment below params to mount data.

# If you have data on your host, if you want to mount that as volume. Please update below paths
# volumes - path in this section will create a volume for you based on host path provided
# volumeMounts - mountPath in this section will mount above volume at specified location
#ks param set ${COMPONENT} volumes '[{ "name": "vol", "hostPath": { "path": "<path_on_host_data>" }}]'
#ks param set ${COMPONENT} volumeMounts '[{ "name": "vol", "mountPath": "<mount_path_in_container"}]'

# Deploy to your cluster.
ks apply default
