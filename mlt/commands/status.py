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
# Unless required by applicable law or agreed to in writing, software`
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: EPL-2.0
#
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

from mlt.commands import Command
from mlt.utils import config_helpers, files, process_helpers, sync_helpers


class StatusCommand(Command):
    def __init__(self, args):
        super(StatusCommand, self).__init__(args)
        self.config = config_helpers.load_config()

    def action(self):
        push_file = '.push.json'
        if os.path.isfile(push_file):
            with open(push_file, 'r') as f:
                data = json.load(f)
        else:
            print("This app has not been deployed yet")
            sys.exit(1)

        namespace = self.config['namespace']
        jobs = files.get_deployed_jobs()

        # display status for only `--count` amount of jobs
        for job in jobs[:self.args["--count"]]:
            job_name = job.replace('k8s/', '')
            print('Job: {} -- Creation Time: {}'.format(
                job_name, datetime.fromtimestamp(
                    int(os.path.getmtime(job)), timezone.utc)))

            self._display_status(job_name, namespace)
            # TODO: something more fancy to separate different statuses?
            print('')

    def _display_status(self, job, namespace):
        """detects what kind of job was deployed and calls the correct
           status display function
        """
        status_options = {
            "job": self._generic_status,
            "tfjob": self._tfjob_status,
            "pytorchjob": self._pytorchjob_status,
            # experiments have yaml templates but also a bash script to call
            "experiment": self._custom_status
        }

        # if we have more than 1 k8 object created and types don't match
        # go with a custom job type since we won't know what kubectl call
        # to make to get status from everything
        job_types, all_same_job_type = files.get_job_kinds()
        if job_types and len(job_types) > 1 and not all_same_job_type:
            job_types = "custom"
        elif job_types:
            job_types = job_types.pop()

        try:
            status_options.get(job_types, self._custom_status)(job, namespace)
        except subprocess.CalledProcessError as e:
            print("Error while getting app status: {}".format(e.output))
            sys.exit(1)

    def _custom_status(self, job, namespace):
        """runs `make status` on any special deployment
           Special deployment is defined as any one of the following:
                1. Doesn't have deployment yaml
                2. Has deployment yaml but many deployments of different kinds
        """
        user_env = dict(os.environ, NAMESPACE=namespace, JOB_NAME=job)
        try:
            output = subprocess.check_output(["make", "status"],
                                             env=user_env,
                                             stderr=subprocess.STDOUT)
            print(output.decode("utf-8").strip())
            if sync_helpers.get_sync_spec() is not None:
                # format the string before passing it print so that the string
                # is evaluated correctly
                print("\nSYNC STATUS\n{}".format(
                    'This app is being watched by sync'))
        except subprocess.CalledProcessError as e:
            if "No rule to make target `status'" in str(e.output):
                # TODO: when we have a template updating capability, add a
                # note recommending that he user update's their template to
                # get the status command
                print("This app does not support the `mlt status` command. "
                      "No `status` target was found in the Makefile.")

    def _generic_status(self, job, namespace):
        """displays simple pod information"""
        status = process_helpers.run_popen(
            ["kubectl", "get", "pods", "--namespace", namespace,
             "-o", "wide", "-a", "-l", "job-name={}".format(job)],
            stdout=True, stderr=True)
        status.wait()

    def _tfjob_status(self, job, namespace):
        """displays status for a TFJob deployment"""
        print('tfjob')

    def _pytorchjob_status(self, job, namespace):
        """displays status for a PyTorchJob deployment"""
        print('pytorch')
