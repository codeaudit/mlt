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

SHELL := /bin/bash

.PHONY: \
	build \
	ksync-watch \
	main \
	status \
	sync-create \
	sync-delete \
	sync-reload

all: main

main: main.py
	@echo "Should run linting and tests before submitting application"

build:
	docker build --build-arg HTTP_PROXY=${HTTP_PROXY} --build-arg HTTPS_PROXY=${HTTPS_PROXY} --build-arg http_proxy=${http_proxy} --build-arg https_proxy=${https_proxy} -t ${CONTAINER_NAME} .

# targets starting with 'ksync' are not meant to be exposed by mlt directly
ksync-watch:
	@if ! pgrep -x "ksync" > /dev/null; then echo `ksync watch -d`; sleep 5; fi

sync-create: ksync-watch
	@ksync create --name ${SYNC_SPEC} -n ${NAMESPACE} --selector=pytorch_job_name=${JOB_NAME} `pwd` /src/app

sync-reload: ksync-watch
	@ksync reload ${SYNC_SPEC}

sync-delete: ksync-watch
	@ksync delete ${SYNC_SPEC}

