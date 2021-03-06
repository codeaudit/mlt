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

from __future__ import print_function

import pytest

import uuid
from mlt.commands.logs import LogsCommand

from test_utils.io import catch_stdout


@pytest.fixture
def json_mock(patch):
    return patch('log_helpers.json')


@pytest.fixture
def open_mock(patch):
    return patch('open')


@pytest.fixture
def sleep_mock(patch):
    return patch('log_helpers.sleep')


@pytest.fixture
def process_helpers(patch):
    return patch('log_helpers.process_helpers.run_popen')


@pytest.fixture
def os_path_mock(patch):
    return patch('log_helpers.os.path')


@pytest.fixture
def check_for_pods_readiness_mock(patch):
    return patch('log_helpers.check_for_pods_readiness')


@pytest.fixture
def verify_init(patch):
    return patch('config_helpers.load_config')


def test_logs_get_logs(json_mock, open_mock, verify_init, sleep_mock,
                       check_for_pods_readiness_mock,
                       process_helpers, os_path_mock):
    run_id = str(uuid.uuid4())
    os_path_mock.exists.return_value = True
    json_mock_data = {
        'last_remote_container': 'gcr.io/app_name:container_id',
        'last_push_duration': 0.18889,
        'app_run_id': run_id}
    json_mock.load.return_value = json_mock_data
    logs_command = LogsCommand({'logs': True, '--since': '1m', '--retries': 5})
    logs_command.config = {'name': 'app', 'namespace': 'namespace'}

    check_for_pods_readiness_mock.return_value = True
    process_helpers.return_value.poll.return_value = 0
    process_helpers.return_value.communicate.return_value = ("log output", '')

    with catch_stdout() as caught_output:
        logs_command.action()
        output = caught_output.getvalue().strip()

    assert output == "log output"


def test_logs_no_push_json_file(open_mock, verify_init, sleep_mock,
                                process_helpers, os_path_mock):
    os_path_mock.exists.return_value = False
    logs_command = LogsCommand({'logs': True, '--since': '1m', '--retries': 5})
    logs_command.config = {'name': 'app', 'namespace': 'namespace'}

    with catch_stdout() as caught_output:
        with pytest.raises(SystemExit):
            logs_command.action()
        output = caught_output.getvalue()

    assert "This app has not been deployed yet" in output


def test_logs_corrupted_app_run_id(json_mock, open_mock, sleep_mock,
                                   verify_init, process_helpers, os_path_mock):
    run_id = '31dea6fc'
    os_path_mock.exists.return_value = True
    json_mock_data = {
        'last_remote_container': 'gcr.io/app_name:container_id',
        'last_push_duration': 0.18889,
        'app_run_id': run_id}
    json_mock.load.return_value = json_mock_data
    logs_command = LogsCommand({'logs': True, '--since': '1m', '--retries': 5})
    logs_command.config = {'name': 'app', 'namespace': 'namespace'}

    with catch_stdout() as caught_output:
        with pytest.raises(SystemExit):
            logs_command.action()
        output = caught_output.getvalue()

    assert"Please re-deploy app again, something went wrong." in output


def test_logs_command_not_found(json_mock, open_mock, sleep_mock,
                                check_for_pods_readiness_mock, verify_init,
                                process_helpers, os_path_mock):
    run_id = str(uuid.uuid4())
    os_path_mock.exists.return_value = True
    json_mock_data = {
        'last_remote_container': 'gcr.io/app_name:container_id',
        'last_push_duration': 0.18889,
        'app_run_id': run_id}
    json_mock.load.return_value = json_mock_data
    logs_command = LogsCommand({'logs': True, '--since': '1m', '--retries': 5})
    logs_command.config = {'name': 'app', 'namespace': 'namespace'}
    check_for_pods_readiness_mock.return_value = True
    command_not_found = str('/bin/sh: kubetail: command not found')
    process_helpers.return_value.poll.return_value = 1
    process_helpers.return_value.communicate.return_value = (None,
                                                             command_not_found)
    with catch_stdout() as caught_output:
        with pytest.raises(SystemExit):
            logs_command.action()
        output = caught_output.getvalue()

    assert 'It is a prerequisite' in output


def test_logs_no_logs_found(json_mock, open_mock, sleep_mock,
                            check_for_pods_readiness_mock, verify_init,
                            process_helpers, os_path_mock):
    run_id = str(uuid.uuid4())
    os_path_mock.exists.return_value = True
    json_mock_data = {'last_remote_container': 'gcr.io/app_name:container_id',
                      'last_push_duration': 0.18889,
                      'app_run_id': run_id}
    json_mock.load.return_value = json_mock_data
    logs_command = LogsCommand({'logs': True, '--since': '1m', '--retries': 5})
    logs_command.config = {'name': 'app', 'namespace': 'namespace'}
    check_for_pods_readiness_mock.return_value = False
    with catch_stdout() as caught_output:
        logs_command.action()
        output = caught_output.getvalue()
    assert "No logs found for this job." in output


def test_logs_keyboardinterrupt(json_mock, open_mock, verify_init, sleep_mock,
                                check_for_pods_readiness_mock, process_helpers,
                                os_path_mock):
    run_id = str(uuid.uuid4())
    os_path_mock.exists.return_value = True
    json_mock_data = {
        'last_remote_container': 'gcr.io/app_name:container_id',
        'last_push_duration': 0.18889,
        'app_run_id': run_id}
    json_mock.load.return_value = json_mock_data
    logs_command = LogsCommand({'logs': True, '--since': '1m', '--retries': 5})
    logs_command.config = {'name': 'app', 'namespace': 'namespace'}

    check_for_pods_readiness_mock.return_value = True
    process_helpers.side_effect = KeyboardInterrupt
    with catch_stdout():
        with pytest.raises(SystemExit):
            logs_command.action()
