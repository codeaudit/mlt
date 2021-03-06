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

# NOTE: UNUSED BUT KEEPING AROUND FOR FUTURE LOCAL CLUSTER CREATION

if [ $# -ne 2 ]
then
	echo "usage: wait-port <ip> <port>" 1>&2
	exit 1
fi

ip=$1
port=$2

until nc -z $ip $port
do
	# One second delay between retries.
	sleep 1
done
