# Git-Annex-Adapter
# Copyright (C) 2017 Alper Nebi Yasak
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import subprocess
import unittest

from git_annex_adapter.process import Process
from git_annex_adapter.process import ProcessRunner

from tests.utils import TempDirTestCase
from tests.utils import TempRepoTestCase
from tests.utils import TempAnnexTestCase


class TestProcessesInEmptyDirectory(TempDirTestCase):
    """Test processes running in an empty directory"""
    def test_runner_git_status(self):
        """ProcessRunner should raise on called process errors"""
        runner = ProcessRunner(['git'], workdir=self.tempdir)
        with self.assertRaises(subprocess.CalledProcessError) as cm:
            runner('status', '-sb')
        self.assertIn(
            "fatal: Not a git repository",
            cm.exception.stderr,
        )

    def test_runner_git_version(self):
        """ProcessRunner should return subprocess.CompletedProcess"""
        runner = ProcessRunner(['git'], workdir=self.tempdir)
        proc = runner('version')
        self.assertIsInstance(proc, subprocess.CompletedProcess)
        self.assertIn('git version', proc.stdout)


class TestProcessesInAnnexRepo(TempAnnexTestCase):
    """Test processes running in an empty git-annex repository"""
    def test_process_git_status(self):
        """One-shot process output should be correct"""
        with Process(['git', 'status'], self.tempdir) as proc:
            stdout = proc.communicate_lines()
            self.assertEqual(stdout, [
                'On branch master',
                '',
                'Initial commit',
                '',
                'nothing to commit (create/copy files '
                + 'and use "git add" to track)',
            ])

    def test_process_annex_metadata_batch(self):
        """Process should be able to read one line per line"""
        with Process(
            ['git', 'annex', 'metadata', '--batch', '--json'],
            self.tempdir,
        ) as proc:
            lines = proc.communicate_lines(
                '{"key":"SHA256E-s0--0"}'
            )
            self.assertEqual(lines, ['{'
                '"command":"metadata",'
                '"note":"",'
                '"success":true,'
                '"key":"SHA256E-s0--0",'
                '"file":null,'
                '"fields":{}'
            '}'])

    def test_process_annex_info_batch(self):
        """Process should be able to read multiple lines per line"""
        with Process(
            ['git', 'annex', 'info', '--batch'],
            self.tempdir,
        ) as proc:
            lines_here = proc.communicate_lines('here')
            self.assertEqual(lines_here, [
                'remote annex keys: 0',
                'remote annex size: 0 bytes',
            ])
            lines_dot = proc.communicate_lines('.')
            self.assertEqual(lines_dot, [
                'directory: .',
                'local annex keys: 0',
                'local annex size: 0 bytes',
                'annexed files in working tree: 0',
                'size of annexed files in working tree: 0 bytes',
                'numcopies stats:',
                'repositories containing these files: 0',
            ])

if __name__ == '__main__':
    unittest.main()
