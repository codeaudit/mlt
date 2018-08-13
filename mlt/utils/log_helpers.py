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
import sys
import subprocess

from termcolor import colored
from time import sleep

from mlt.utils import process_helpers


def call_logs(config, args):
    """
    This method will check for `.push.json`
    and provides run-id to _get_logs method to
    fetch logs.
    """
    if os.path.exists('.push.json'):
        with open('.push.json', 'r') as f:
            data = json.load(f)
    else:
        print("This app has not been deployed yet, "
              "there are no logs to display.")
        sys.exit(1)

    app_run_id = data['app_run_id'].split("-")

    if len(app_run_id) < 2:
        print("Please re-deploy app again, something went wrong.")
        sys.exit(1)

    prefix = "-".join([config["name"], app_run_id[0], app_run_id[1]])

    namespace = config['namespace']
    retires = args["--retries"]

    # check for pod readiness before fetching logs.
    running = check_for_pods_readiness(namespace, prefix, retires)

    if running:
        since = args["--since"]
        _get_logs(prefix, since, namespace)
    else:
        print("No logs found for this job.")


def _get_logs(prefix, since, namespace):
    """
    Fetches logs using kubetail
    """
    log_cmd = ["kubetail", prefix, "--since", since, "--namespace", namespace]
    try:
        logs = process_helpers.run_popen(log_cmd,
                                         stdout=True,
                                         stderr=subprocess.PIPE)

        output, error_msg = logs.communicate()
        if output:
            print(output)
        if error_msg:
            if 'command not found' in error_msg:
                print(colored("Please install `{}`. "
                      "It is a prerequisite "
                              "for `mlt logs` to work"
                              .format(error_msg.split()[1]), 'red'))
            else:
                print(colored(error_msg, 'red'))
            sys.exit(1)
    except KeyboardInterrupt:
        sys.exit()


def check_for_pods_readiness(namespace, filter_tag, retries):
    print("Checking for pod(s) readiness")
    tries = 0

    pods_found = 0
    pods_running = 0
    while True:
        if tries == retries:
            print("Max retries Reached.")
            break
        try:
            kubectl_cmd = ["kubectl", "get", "pods", "--namespace", namespace]
            pods = process_helpers.run_popen(kubectl_cmd)\
                .stdout.read().strip().splitlines()

            if not pods:
                tries += 1
                print("Retrying {}/{} \r".format(tries, retries)),
                sleep(1)
                continue
            else:
                for pod in pods:
                    if filter_tag in pod.decode('utf-8'):
                        pods_found += 1
                        status = pod.split()[2].strip().decode('utf-8')
                        if status in ['Running', 'Completed']:
                            pods_running += 1

            if pods_running == pods_found and pods_found > 0:
                break
            else:
                pods_found = 0
                pods_running = 0
                tries += 1
                print("Retrying {}/{} \r".format(tries, retries)),
                sleep(1)
        except KeyboardInterrupt:
            sys.exit()

    return pods_running > 0
