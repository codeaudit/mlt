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
import pytest
import sys
from mock import MagicMock
from subprocess import CalledProcessError

from mlt.utils.process_helpers import prevent_deadlock, run, run_popen
from test_utils.io import catch_stdout


@pytest.fixture
def check_output_mock(patch):
    return patch('check_output')


@pytest.fixture
def popen_mock(patch):
    return patch('Popen')


def test_run_no_cwd(check_output_mock):
    """Assert a command was called with no current working dir
       This command should return the value of `bar`
    """
    check_output_mock.return_value.decode.return_value = 'bar'
    output = run('ls')
    assert output == 'bar'


def test_run_cwd(check_output_mock):
    """Assert a command was called with /tmp as working dir
       This command should return the value of `foo`
    """
    check_output_mock.return_value.decode.return_value = 'foo'
    output = run('ls', '/tmp')
    assert output == 'foo'


def test_run_error(check_output_mock):
    """There was a bad command made, therefore no output"""
    check_output_mock.side_effect = CalledProcessError(
        returncode=2, cmd='Bad Command!')
    # pytest.set_trace()
    with catch_stdout() as caught_output:
        with pytest.raises(SystemExit):
            run('ls')
        output = caught_output.getvalue().strip()
    # since we're mocking CalledProcessError call, not sure we can simulate
    # exception raised by actual check_output call, so e.output is None
    assert output == 'None'


def test_run_popen(popen_mock):
    """Popen call should succeed"""
    popen_mock.return_value = 0
    result = run_popen(['ls', '/tmp'])
    assert result == 0


def test_run_popen_shell_str(popen_mock):
    """Popen call should succeed"""
    popen_mock.return_value = 0
    result = run_popen('ls /tmp', shell=True)
    assert result == 0


def test_run_popen_shell_list(popen_mock):
    """Popen call should succeed"""
    popen_mock.return_value = 0
    result = run_popen(['ls', '/tmp'], shell=True)
    assert result == 0


def test_run_popen_invalid_cmd(popen_mock):
    """Assert passing not a string or list causes SystemExit"""
    with pytest.raises(SystemExit) as pytest_raised_err:
        run_popen(0)
    assert pytest_raised_err.value.code == 1


def test_run_popen_failed_cmd(popen_mock):
    """If the cmd isn't valid assert some sort of error output + SystemExit"""
    bad_cmd = "foo bar"
    bad_cmd_output = "Not a valid command"
    popen_mock.side_effect = CalledProcessError(
        returncode=2, cmd=bad_cmd, output=bad_cmd_output)
    with catch_stdout() as caught_output:
        with pytest.raises(SystemExit):
            run_popen(bad_cmd)
        output = caught_output.getvalue().strip()
    assert output == bad_cmd_output


@pytest.mark.parametrize("pipe_output", [
    MagicMock(side_effect=["One line of output", ""], length=3),
    MagicMock(side_effect=["First line", "Second line", ""], length=4)])
def test_prevent_deadlock(pipe_output):
    """Assert that we iterate over the correct amount of output
       from the 'subprocess'
    """
    proc_mock = MagicMock()
    proc_mock.stdout.readline = pipe_output
    with prevent_deadlock(proc_mock):
        pass
    # python2 treats `iter()` a bit differently and won't count the
    # sentinel as an iteration loop
    if sys.version_info[0] < 3:
        pipe_output.length -= 1
    assert proc_mock.stdout.readline.call_count == pipe_output.length
