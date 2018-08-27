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
        jobs = files.get_deployed_jobs()
        if not jobs:
            print("This app has not been deployed yet.")
            sys.exit(1)
        else:
            if self.args.get('--job-name'):
                job_name = self.args['--job-name']
                if job_name in jobs:
                    self._undeploy_jobs(namespace, job_name)
                else:
                    print('Job name {} not found in: {}'
                          .format(job_name, jobs))
                    sys.exit(1)
            elif self.args.get('--all') or len(jobs) == 1:
                self._undeploy_jobs(namespace, jobs, all_jobs=True)
            else:
                print("Multiple jobs are found under this application, "
                      "please try `mlt undeploy --all` or specify a single "
                      "job to undeploy using "
                      "`mlt undeploy --job-name <job-name>`")
                sys.exit(1)

    def _undeploy_jobs(self, namespace, jobs, all_jobs=False):
        """undeploy the jobs passed to us
           jobs: 1 or more jobs to undeploy
        """
        # simplify logic by `looping` over all jobs even if there's just 1
        if not isinstance(jobs, list):
            jobs = [jobs]

        # if any job isn't custom, we are safe to recursive delete k8s objs
        # as at least 1 folder will be undeployed this way
        recursive_delete = False
        for job in jobs:
            # there could be a case where the same template has both custom
            # and non-custom jobs to undeploy. Need to handle both cases
            if files.is_custom('undeploy:', job):
                self._custom_undeploy(job)
            else:
                recursive_delete = True
        if recursive_delete:
            process_helpers.run(
                ["kubectl", "--namespace", namespace, "delete", "-f",
                 "k8s", "--recursive"],
                raise_on_failure=True)
        # we won't delete job folders unless undeploy was successful
        # TODO: have this not be in a loop
        for job in jobs:
            self.remove_job_dir(os.path.join('k8s', job))

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
