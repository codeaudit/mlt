#!/bin/bash
#
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

# install ksonnet + kubeflow so we can support TFJob

NAMESPACE=kubeflow
VERSION=3920d1402f40455c0f3e5f54ea4cc8142c23c2c8
APP_NAME=kubeflow
# by default we'll use our hyperkube config
# TODO: delete the hyperkube config
# : "${KUBECONFIG:=../resources/config.yaml}"
# workaround for https://github.com/ksonnet/ksonnet/issues/298
export USER=root

./scripts/ksonnet_install_linux.sh

# create namespace if doesn't exist yet
kubectl create namespace $NAMESPACE -v=7 || true

# create basic ks app
cd /tmp
ks init $APP_NAME
cd $APP_NAME
ks env set default --namespace $NAMESPACE

# install kubeflow components for TFJob support
ks registry add kubeflow github.com/kubeflow/kubeflow/tree/$VERSION/kubeflow
ks pkg install kubeflow/core@$VERSION
ks pkg install kubeflow/tf-job@$VERSION
ks pkg install kubeflow/pytorch-job@$VERSION
ks generate kubeflow-core kubeflow-core
ks generate pytorch-operator pytorch-operator
ks apply default -c kubeflow-core
ks apply default -c pytorch-operator
