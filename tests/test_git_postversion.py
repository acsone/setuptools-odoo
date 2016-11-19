# -*- coding: utf-8 -*-
# Copyright © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import os
import unittest

from setuptools_odoo import git_postversion
from setuptools_odoo import manifest

from . import DATA_DIR


class TestGitPostversion(unittest.TestCase):

    def test_addon1(self):
        """ addon1 has 2 commit after version 8.0.1.0.0 """
        addon1_dir = os.path.join(DATA_DIR, 'addon1')
        version = git_postversion.get_git_postversion(addon1_dir)
        assert version == '8.0.1.0.0.99.dev2'

    def test_addon2(self):
        """ addon2 has not changed since 8.0.1.0.1 """
        addon2_dir = os.path.join(DATA_DIR, 'addon2')
        version = git_postversion.get_git_postversion(addon2_dir)
        assert version == '8.0.1.0.1'

    def test_addon2_uncommitted_version_change(self):
        """ test with a local uncommitted version change """
        addon2_dir = os.path.join(DATA_DIR, 'addon2')
        manifest_path = os.path.join(addon2_dir, '__openerp__.py')
        manifest = open(manifest_path).read()
        try:
            open(manifest_path, "w").write(manifest.replace("8.0.1.0.1",
                                                            "8.0.1.0.2"))
            version = git_postversion.get_git_postversion(addon2_dir)
            assert version == '8.0.1.0.2.dev1'
        finally:
            open(manifest_path, "w").write(manifest)

    def test_addon1_uncommitted_change(self):
        """ test with a local uncommitted change without version change """
        addon1_dir = os.path.join(DATA_DIR, 'addon1')
        manifest_path = os.path.join(addon1_dir, '__openerp__.py')
        manifest = open(manifest_path).read()
        try:
            open(manifest_path, "w").write(manifest.replace("summary",
                                                            "great summary"))
            version = git_postversion.get_git_postversion(addon1_dir)
            assert version == '8.0.1.0.0.99.dev3'
        finally:
            open(manifest_path, "w").write(manifest)

    def test_no_manifest(self):
        with self.assertRaises(manifest.NoManifestFound):
            git_postversion.get_git_postversion(DATA_DIR)
