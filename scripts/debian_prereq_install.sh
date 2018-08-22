#! /bin/bash
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

# TODO: is this even necessary? Users should have `git` already
# jq is needed for tensorboard
# openssh is needed for horovod
apt-get install git jq openssh-server openssh-client

# install tfjob, pytorch operators, ks
if [[ `kubectl get crd | grep -E 'tfjobs\.kubeflow\.org|pytorchjobs\.kubeflow\.org' -c` -ne "2" || ! `command -v ks` ]]; then
	GITHUB_TOKEN=${GITHUB_TOKEN} ./scripts/kubeflow_install.sh
fi

# install ksync
if [ ! "$(command -v ksync)" ]; then
	./scripts/ksync_install.sh
fi

# install kubetail
if [ ! "$(command -v kubetail)" ]; then
	wget -O /usr/local/bin/kubetail https://raw.githubusercontent.com/johanhaleby/kubetail/1.6.1/kubetail
	chmod +x /usr/local/bin/kubetail
fi

# Install experiments CRDs
if [ `kubectl get crd | grep -E 'experiments\.ml\.intel\.com' -c` -ne "1" ]; then
	./scripts/experiments_crd_install.sh
fi
