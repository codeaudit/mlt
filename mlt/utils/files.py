#
# -*- coding: utf-8 -*-
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

import json
import os
import shutil


def fetch_action_arg(action, arg):
    """fetches data from command json files"""
    action_json = '.{}.json'.format(action)
    if os.path.isfile(action_json):
        with open(action_json) as f:
            return json.load(f).get(arg)


def is_custom(target):
    custom = False
    if os.path.isfile('Makefile'):
        with open('Makefile') as f:
            for line in f:
                if line.startswith(target):
                    custom = True
                    break
    return custom


def get_deployed_jobs():
    """get the list of the deployed jobs."""
    return [d for d in os.listdir('k8s')
            if os.path.isdir(os.path.join('k8s', d))]


def create_job_subdir(job_name):
    """create a sub-directory in k8s with the given job name."""
    job_sub_dir = 'k8s/{}'.format(job_name)
    if not os.path.exists(job_sub_dir):
        os.makedirs(job_sub_dir)
    return job_sub_dir


def remove_job_dir(job_dir):
    # remove the job sub-directory from k8s
    shutil.rmtree(job_dir)
