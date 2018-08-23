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

import os
import subprocess
import sys
import shutil

from termcolor import colored

from mlt.commands import Command
from mlt.utils import config_helpers, process_helpers, files, sync_helpers


class UndeployCommand(Command):
    def __init__(self, args):
        super(UndeployCommand, self).__init__(args)
        self.config = config_helpers.load_config()

    def action(self):
        """deletes current kubernetes namespace"""

        if sync_helpers.get_sync_spec() is not None:
            print(colored("This app is currently being synced, please run "
                          "`mlt sync delete` to unsync first", 'red'))
            sys.exit(1)

        namespace = self.config['namespace']
        jobs_list = files.get_deployed_jobs()
        if not jobs_list:
            print("This app has not been deployed yet.")
            sys.exit(1)
        else:
            if self.args.get('--all'):
                self._undeploy_all(namespace, jobs_list)
            elif self.args.get('--job-name'):
                job_name = self.args['--job-name']
                if job_name in jobs_list:
                    self._undeploy_job(namespace, job_name)
                else:
                    print('Job-name {} not found in: {}'
                          .format(job_name, jobs_list))
                    sys.exit(1)
            elif len(jobs_list) == 1:
                self._undeploy_job(namespace, jobs_list.pop())
            else:
                print("Multiple jobs are found under this application, "
                      "please try `mlt undeploy --all` or specify a single"
                      " job to undeploy using "
                      "`mlt undeploy --job-name <job-name>`")
                sys.exit(1)

    def _undeploy_all(self, namespace, jobs_list):
        """undeploy all jobs."""
        for job in jobs_list:
            self._undeploy_job(namespace, job)

    def _undeploy_job(self, namespace, job_name):
        """undeploy the given job name"""
        job_dir = "k8s/{}".format(job_name)
        if files.is_custom('undeploy:'):
            self._custom_undeploy(job_name)
        else:
            process_helpers.run(
                ["kubectl", "--namespace", namespace, "delete", "-f",
                 job_dir, "--recursive"],
                raise_on_failure=True)
        self.remove_job_dir(job_dir)

    def remove_job_dir(self, job_dir):
        """remove the job sub-directory from k8s."""
        shutil.rmtree(job_dir)

    def _custom_undeploy(self, job_name):
        """
        Custom undeploy uses the make targets to perform operation.
        """
        # Adding USER env because
        # https://github.com/ksonnet/ksonnet/issues/298
        user_env = dict(os.environ, JOB_NAME=job_name, USER='root')
        try:
            output = subprocess.check_output(["make", "undeploy"],
                                             env=user_env,
                                             stderr=subprocess.STDOUT)
            print(output.decode("utf-8").strip())
        except subprocess.CalledProcessError as e:
            print("Error while undeploying app: {}".format(e.output))
