# -*- coding: utf-8 -*-
# Copyright © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import filecmp
import os
import shutil
import tempfile
import unittest

from setuptools_odoo import make_default_setup

from . import DATA_DIR


class TestMakeDefaultSetup(unittest.TestCase):

    def _assert_no_diff(self, dc):
        def _filter(l):
            return [i for i in l
                    if not i.endswith('.pyc') and
                    not i.endswith('.egg-info') and
                    not i.endswith('.eggs')]
        if dc.right.endswith('addon4'):
            # in addon4, we have a customized
            # setup.py to test depends and external_dependencies overrides
            return
        self.assertFalse(_filter(dc.left_only),
                         "missing %s in %s" % (dc.left_only, dc.right))
        self.assertFalse(_filter(dc.right_only),
                         "unexpected %s in %s" % (dc.right_only, dc.right))
        self.assertFalse(_filter(dc.diff_files),
                         "differing %s in %s" % (dc.diff_files, dc.right))
        for sub_dc in dc.subdirs.values():
            self._assert_no_diff(sub_dc)

    def test1(self):
        expected_dir = os.path.join(DATA_DIR, 'setup_reusable_addons')
        generated_dir = os.path.join(DATA_DIR, 'setup')
        make_default_setup.main(['--addons-dir', DATA_DIR, '-f'])
        dc = filecmp.dircmp(expected_dir, generated_dir)
        try:
            self._assert_no_diff(dc)
        finally:
            shutil.rmtree(generated_dir)

    def test_make_ns_pkg_dirs_1(self):
        opj = os.path.join
        tmpdir = tempfile.mkdtemp()
        try:
            d = make_default_setup.make_ns_pkg_dirs(
                tmpdir, 'odoo_addons', False, True)
            self.assertEqual(d, opj(tmpdir, 'odoo_addons'))
            self.assertTrue(os.path.isdir(d))
            self.assertTrue(os.path.isfile(opj(d, '__init__.py')))
        finally:
            shutil.rmtree(tmpdir)

    def test_make_ns_pkg_dirs_2(self):
        opj = os.path.join
        tmpdir = tempfile.mkdtemp()
        try:
            d = make_default_setup.make_ns_pkg_dirs(
                tmpdir, 'odoo.addons', False, True)
            self.assertEqual(d, opj(tmpdir, 'odoo', 'addons'))
            self.assertTrue(os.path.isdir(d))
            self.assertTrue(
                os.path.exists(opj(tmpdir, 'odoo', '__init__.py')))
            self.assertTrue(os.path.isfile(opj(d, '__init__.py')))
        finally:
            shutil.rmtree(tmpdir)

    def test_make_ns_pkg_dirs_3(self):
        opj = os.path.join
        tmpdir = tempfile.mkdtemp()
        try:
            d = make_default_setup.make_ns_pkg_dirs(
                tmpdir, 'odoo.addons', False, False)
            self.assertEqual(d, opj(tmpdir, 'odoo', 'addons'))
            self.assertTrue(os.path.isdir(d))
            self.assertFalse(
                os.path.exists(opj(tmpdir, 'odoo', '__init__.py')))
            self.assertFalse(os.path.exists(opj(d, '__init__.py')))
        finally:
            shutil.rmtree(tmpdir)


if __name__ == '__main__':
    unittest.main()
