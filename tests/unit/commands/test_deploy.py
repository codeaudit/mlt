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

import uuid
import pytest
from conditional import conditional
from mock import call, MagicMock

from mlt.commands.deploy import DeployCommand
from test_utils.io import catch_stdout


@pytest.fixture
def sleep(patch):
    return patch('time.sleep')


@pytest.fixture
def call_logs(patch):
    return patch('log_helpers.call_logs')


@pytest.fixture
def fetch_action_arg(patch):
    return patch('files.fetch_action_arg', MagicMock(return_value='output'))


@pytest.fixture
def kube_helpers(patch):
    return patch('kubernetes_helpers')


@pytest.fixture
def json_mock(patch):
    return patch('json')


@pytest.fixture
def open_mock(patch):
    return patch('open')

# PROCESS_HELPERS MOCKS


@pytest.fixture(autouse=True)
def process_helpers_mock(patch):
    # mock every outside process generally, specific mocks below
    return patch('process_helpers')


@pytest.fixture
def run_popen_mock(patch):
    run_popen_mock = MagicMock()
    run_popen_mock.return_value.poll.return_value = 0
    return patch('process_helpers.run_popen', run_popen_mock)


@pytest.fixture
def process_helpers_run_mock(patch):
    run_mock = MagicMock(side_effect=SystemExit)
    # want to test that kubectl apply failed
    return patch('process_helpers.run', run_mock)


# END PROCESS_HELPERS MOCKS


@pytest.fixture
def progress_bar(patch):
    progress_mock = MagicMock()
    progress_mock.duration_progress.side_effect = lambda x, y, z: print(
        'Pushing ')
    return patch('progress_bar', progress_mock)


@pytest.fixture
def template(patch):
    return patch('Template')


@pytest.fixture
def verify_build(patch):
    return patch('build_helpers.verify_build')


@pytest.fixture
def verify_init(patch):
    return patch('config_helpers.load_config')


@pytest.fixture
def subprocess_mock(patch):
    return patch('check_output')


@pytest.fixture
def walk_mock(patch):
    return patch('os.walk', MagicMock(return_value=['foo', 'bar']))


@pytest.fixture
def yaml(patch):
    return patch('yaml.load')


@pytest.fixture
def get_sync_spec_mock(patch):
    return patch('sync_helpers.get_sync_spec')


@pytest.fixture
def is_custom_mock(patch):
    return patch('files.is_custom')


def deploy(no_push, skip_crd_check, interactive, extra_config_args, retries=5,
           template='test', logs=False, verbose=False, catch_exception=None):
    deploy = DeployCommand(
        {'deploy': True, '--no-push': no_push,
         '--skip-crd-check': skip_crd_check,
         '--interactive': interactive, '--retries': retries,
         '--logs': logs, '--verbose': verbose})
    deploy.config = {'name': 'app',
                     'namespace': 'namespace',
                     'template': template}

    deploy.config.update(extra_config_args)

    with catch_stdout() as caught_output:
        with conditional(catch_exception, pytest.raises(catch_exception)):
            deploy.action()
        output = caught_output.getvalue()
    return output


def verify_successful_deploy(output, did_push=True, interactive=False,
                             pod_count=2, verbose=False):
    """assert pushing, deploying, then objs created, then pushed"""
    pushing = output.find('Pushing ')
    push_skip = output.find('Skipping image push')
    deploying = output.find('Deploying ')
    inspecting = output.find('Inspect created objects by running:\n')
    pushed = output.find('Pushed app to ')
    if pod_count == 1:
        pod_connect = output.find('Connecting to pod...')
    else:
        pod_connect = output.find('watch until pods are `Running`')

    if did_push:
        # we don't print `pushing ####` stuff in `verbose` mode
        if not verbose:
            assert all(var >= 0 for var in (
                deploying, inspecting, pushing, pushed))
            assert deploying < inspecting, pushing < pushed
        else:
            assert all(var >= 0 for var in (
                deploying, inspecting, pushed))
            assert deploying < inspecting, pushed < deploying
    else:
        assert all(var == -1 for var in (pushing, pushed))
        assert all(var >= 0 for var in (deploying, inspecting, push_skip))
        assert push_skip < deploying, deploying < inspecting

    if interactive:
        assert pod_connect > inspecting


@pytest.mark.parametrize("sync_spec", [
    None, 'hello-world'])
@pytest.mark.parametrize("registry", [
    'gcr://projectfoo', 'dockerhub'])
@pytest.mark.parametrize("skip_crd_check", [
    True, False])
@pytest.mark.parametrize("logs", [
    True, False])
@pytest.mark.parametrize("verbose", [
    True, False])
def test_deploy(walk_mock, call_logs, progress_bar, run_popen_mock, open_mock,
                template, kube_helpers, verify_build,
                verify_init, fetch_action_arg, json_mock, get_sync_spec_mock,
                sync_spec, registry, skip_crd_check, logs, verbose):
    """Tests a successful deploy with and without sync_spec, 2 different
       registry types, skipping and not skipping crd_check, and log tailing
    """
    get_sync_spec_mock.return_value = sync_spec
    json_mock.load.return_value = {
        'last_remote_container': 'gcr.io/app_name:container_id',
        'last_push_duration': 0.18889}
    output = deploy(
        no_push=False, skip_crd_check=skip_crd_check,
        interactive=False, logs=logs, verbose=verbose,
        extra_config_args={'registry': registry})
    verify_successful_deploy(output, verbose=verbose)


def test_deploy_without_push(walk_mock, progress_bar, run_popen_mock,
                             open_mock, template, kube_helpers,
                             verify_build, verify_init, fetch_action_arg,
                             json_mock):
    json_mock.load.return_value = {
        'last_remote_container': 'gcr.io/app_name:container_id',
        'last_push_duration': 0.18889}
    output = deploy(
        no_push=True, skip_crd_check=True,
        interactive=False,
        extra_config_args={'registry': 'gcr://projectfoo'})
    verify_successful_deploy(output, did_push=False)


def test_deploy_interactive_one_file(walk_mock, progress_bar, run_popen_mock,
                                     open_mock, template, kube_helpers,
                                     verify_build,
                                     verify_init, fetch_action_arg, sleep,
                                     yaml, json_mock):
    walk_mock.return_value = ['foo']
    yaml.return_value = {
        'template': {'foo': 'bar'}, 'containers': [{'foo': 'bar'}]}
    json_mock.loads.return_value = {'status': {'phase': 'Running'}}
    output = deploy(
        no_push=False, skip_crd_check=True,
        interactive=True,
        extra_config_args={'registry': 'dockerhub'})
    verify_successful_deploy(output, interactive=True, pod_count=1)

    # verify that kubectl commands are specifying namespace
    for call_args in run_popen_mock.call_args_list:
        assert isinstance(call_args, type(call))
        assert isinstance(call_args[0], tuple)
        assert len(call_args[0]) > 0
        command = call_args[0][0]
        if command[0] == "kubectl":
            assert "--namespace" in command


def test_deploy_interactive_two_files(walk_mock, progress_bar, run_popen_mock,
                                      open_mock, template, kube_helpers,
                                      verify_build,
                                      verify_init, fetch_action_arg, sleep,
                                      yaml, json_mock):
    json_mock.loads.return_value = {'status': {'phase': 'Running'}}
    yaml.return_value = {
        'template': {'foo': 'bar'}, 'containers': [{'foo': 'bar'}]}
    output = deploy(
        no_push=False, skip_crd_check=True,
        interactive=True,
        extra_config_args={'registry': 'dockerhub'})
    verify_successful_deploy(output, interactive=True)


def test_deploy_interactive_pod_not_run(walk_mock, progress_bar,
                                        run_popen_mock,
                                        process_helpers_run_mock,
                                        open_mock, template, kube_helpers,
                                        verify_build,
                                        verify_init, fetch_action_arg, sleep,
                                        yaml, json_mock):
    json_mock.loads.return_value = {'status': {'phase': 'Error'}}
    yaml.return_value = {
        'template': {'foo': 'bar'}, 'containers': [{'foo': 'bar'}]}
    with pytest.raises(SystemExit):
        deploy(
            no_push=False, skip_crd_check=True,
            interactive=True,
            extra_config_args={'registry': 'dockerhub'})


def test_deploy_update_app_run_id(open_mock, json_mock):
    run_id = str(uuid.uuid4())
    json_mock_data = {
        'last_remote_container': 'gcr.io/app_name:container_id',
        'last_push_duration': 0.18889}
    json_mock.load.return_value = json_mock_data

    DeployCommand._update_app_run_id(run_id)

    assert json_mock_data['app_run_id'] == run_id


def test_image_push_error(walk_mock, progress_bar, run_popen_mock, open_mock,
                          template, kube_helpers,
                          verify_build, verify_init, fetch_action_arg,
                          json_mock):
    json_mock.load.return_value = {
        'last_remote_container': 'gcr.io/app_name:container_id',
        'last_push_duration': 0.18889}

    # setup mock to induce and error during the deploy
    run_popen_mock.return_value.poll.return_value = 1
    output_str = "normal output..."
    error_str = "error message..."
    build_output = MagicMock()
    build_output.decode.return_value = output_str
    error_output = MagicMock()
    error_output.decode.return_value = error_str
    run_popen_mock.return_value.communicate.return_value = (build_output,
                                                            error_output)

    output = deploy(
        no_push=False, skip_crd_check=True, interactive=False,
        extra_config_args={'registry': 'gcr://projectfoo'},
        catch_exception=SystemExit)

    # assert that we got the normal output, followed by the error message
    output_location = output.find(output_str)
    error_location = output.find(error_str)
    assert all(var >= 0 for var in (output_location, error_location))
    assert output_location < error_location


def test_no_image_found_error(walk_mock, progress_bar, run_popen_mock,
                              open_mock, template, kube_helpers,
                              verify_build, verify_init, fetch_action_arg,
                              json_mock):
    """if we don't have remote_container_name during deploy_new_container
       then throw ValueError
    """
    get_sync_spec_mock.return_value = None
    fetch_action_arg.side_effect = [None, None, None]
    json_mock.load.return_value = {
        'last_remote_container': 'gcr.io/app_name:container_id',
        'last_push_duration': 0.18889}
    deploy(
        no_push=True, skip_crd_check=True, interactive=False,
        extra_config_args={'registry': 'gcr://projectfoo'},
        catch_exception=ValueError)


def test_deploy_custom_deploy(walk_mock, progress_bar, run_popen_mock,
                              open_mock, template, kube_helpers,
                              subprocess_mock, verify_build, is_custom_mock,
                              verify_init, fetch_action_arg, json_mock, ):
    json_mock.load.return_value = {
        'last_remote_container': 'gcr.io/app_name:container_id',
        'last_push_duration': 0.18889}
    expected_output = "Updating configmaps\n" \
                      "Creating non-existent configmaps\n" \
                      "Updating services\n" \
                      "Creating non-existent services\n" \
                      "Updating serviceaccounts\n" \
                      "Creating non-existent serviceaccounts\n" \
                      "Updating clusterrolebindings\n" \
                      "Creating non-existent clusterrolebindings\n" \
                      "Updating pods\n" \
                      "Creating non-existent pods\n"
    subprocess_mock.return_value.decode.return_value = expected_output
    is_custom_mock.return_value = True
    output = deploy(
        no_push=False, skip_crd_check=True,
        interactive=False,
        extra_config_args={'registry': 'gcr://projectfoo',
                           "template_parameters": {
                               "gpus": 0,
                               "num_workers": 1}})
    verify_successful_deploy(output)
    assert expected_output in output


def test_deploy_custom_deploy_interactive(walk_mock, progress_bar,
                                          run_popen_mock, open_mock, template,
                                          kube_helpers, subprocess_mock,
                                          verify_build, is_custom_mock,
                                          verify_init, fetch_action_arg,
                                          json_mock, yaml):
    json_mock.load.return_value = {
        'last_remote_container': 'gcr.io/app_name:container_id',
        'last_push_duration': 0.18889}
    is_custom_mock.return_value = True
    json_mock.loads.return_value = {'status': {'phase': 'Running'}}
    yaml.return_value = {
        'template': {'foo': 'bar'}, 'containers': [{'foo': 'bar'}]}
    output = deploy(
        no_push=False, skip_crd_check=True,
        interactive=True,
        extra_config_args={'registry': 'gcr://projectfoo',
                           "template_parameters": {
                               "gpus": 0,
                               "num_workers": 1}})
    verify_successful_deploy(output, interactive=True)
