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
from mlt.utils import config_helpers, files, sync_helpers


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

            self._custom_status(job_name, namespace)
            # TODO: something more fancy to separate different statuses?
            print('')

    def _custom_status(self, job, namespace):
        """runs `make status` on any special deployment
           Special deployment is defined as any one of the following:
                1. Doesn't have deployment yaml
                TODO: are there more types?
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
            else:
                print("Error while getting app status: {}".format(e.output))
