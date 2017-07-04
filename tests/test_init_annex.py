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

import unittest

from git_annex_adapter import init_annex
from git_annex_adapter.repo import GitAnnexRepo

from tests.utils import TempDirTestCase
from tests.utils import TempRepoTestCase
from tests.utils import TempAnnexTestCase


class TestInitAnnexOnEmptyDir(TempDirTestCase):
    """Test init_annex on an empty temporary directory"""

    def test_init_annex_raises(self):
        """
        git-annex init fails if git isn't already initialized,
        so init_annex should raise an exception.
        """
        with self.assertRaises(Exception):
            init_annex(self.tempdir)


class TestInitAnnexWrongVersions(TempRepoTestCase):
    """Test init_annex with wrong --version arguments"""

    def test_init_annex_version_negative(self):
        """Negative numbers aren't valid versions"""
        with self.assertRaises(ValueError):
            init_annex(self.tempdir, version=-1)

    def test_init_annex_version_string(self):
        """Strings aren't valid versions"""
        with self.assertRaises(ValueError):
            init_annex(self.tempdir, version='foo')


class TestInitAnnexVersion(TempRepoTestCase):
    """Test init_annex with correct version arguments"""

    def test_init_annex_version_five(self):
        """Repository version 5 should be valid"""
        annex_repo = init_annex(self.tempdir, version=5)
        self.assertEqual(annex_repo.config['annex.version'], '5')

    def test_init_annex_version_six(self):
        """Repository version 6 should be valid"""
        annex_repo = init_annex(self.tempdir, version=6)
        self.assertEqual(annex_repo.config['annex.version'], '6')


class TestInitAnnexDescribe(TempRepoTestCase):
    """Test init_annex with correct description arguments"""

    def test_init_annex_description(self):
        """init_annex with description should update uuid.log"""
        repo = init_annex(self.tempdir, description='foo')
        uuid = repo.config['annex.uuid']
        uuid_log_blob = repo.revparse_single('git-annex:uuid.log')
        self.assertIn(
            "{} {} timestamp=".format(uuid, 'foo'),
            str(uuid_log_blob.data),
        )


class TestInitAnnexOnEmptyRepo(TempRepoTestCase):
    """Test init_annex on an empty temporary git repository"""

    def test_init_annex_success(self):
        """
        init_annex should work on a newly initialized git repo
        and return a GitAnnexRepo object. The repository should have
        a git-annex branch as a result.
        """
        annex_repo = init_annex(self.repo.workdir)
        self.assertIsInstance(annex_repo, GitAnnexRepo)
        self.assertIn('git-annex', annex_repo.listall_branches())


class TestInitAnnexOnEmptyAnnexRepo(TempAnnexTestCase):
    """Test init_annex on an empty temporary git-annex repo"""

    def test_init_annex_success(self):
        """
        Running init_annex on an already initialized git-annex
        repository should succeed.
        """
        self.repo = init_annex(self.repo.workdir)


if __name__ == '__main__':
    unittest.main()

