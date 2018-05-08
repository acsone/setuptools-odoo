# -*- coding: utf-8 -*-
# Copyright © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import datetime
import filecmp
import os
import shutil
import subprocess
import tempfile
import textwrap
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

    def test_make_default_setup_metapackage(self):
        tmpdir = tempfile.mkdtemp()
        source_addons_path = os.path.join(
            os.getcwd(),
            'tests', 'data', 'setup_custom_project', 'odoo_addons')
        addons_path = os.path.join(tmpdir, 'tests')
        metapackage_dir = os.path.join(addons_path, 'setup', '_metapackage')
        setup_file = os.path.join(metapackage_dir, 'setup.py')
        version_file = os.path.join(metapackage_dir, 'VERSION.txt')
        today_date = datetime.date.today().strftime('%Y%m%d')
        expected_setup_file = textwrap.dedent("""\
            import setuptools

            with open('VERSION.txt', 'r') as f:
                version = f.read().strip()

            setuptools.setup(
                name="odoo8-addons-tests",
                description="Meta package for tests Odoo addons",
                version=version,
                install_requires=[
                    'odoo8-addon-addon1',
                    'odoo8-addon-addon2',
                ],
                classifiers=[
                    'Programming Language :: Python',
                    'Framework :: Odoo',
                ]
            )
        """)

        try:
            shutil.copytree(source_addons_path, addons_path)
            make_default_setup.make_default_setup_addons_dir(
                addons_path, False, False)
            make_default_setup.make_default_meta_package(
                addons_path, 'tests', odoo_version_override=None)

            with open(setup_file, 'r') as f:
                setup_file_content = f.read()
                self.assertEqual(setup_file_content, expected_setup_file)

            with open(version_file, 'r') as f:
                version = f.read().strip()
                self.assertEqual(version, '8.0.%s.0' % today_date)

            # Create a new addon
            addon1_path = os.path.join(addons_path, 'addon1')
            new_addon_path = os.path.join(addons_path, 'addon99')
            shutil.copytree(addon1_path, new_addon_path)

            make_default_setup.make_default_setup_addons_dir(
                addons_path, False, False)
            make_default_setup.make_default_meta_package(
                addons_path, 'tests', odoo_version_override=None)

            with open(version_file, 'r') as f:
                version = f.read().strip()
                self.assertEqual(
                    version, '8.0.%s.1' % today_date,
                    msg="The version should have been incremented")
        finally:
            shutil.rmtree(tmpdir)


def test_make_default_setup_commit(tmpdir):
    with tmpdir.as_cwd():
        subprocess.check_call(['git', 'init'])
        make_default_setup.main(['--addons-dir', '.', '--commit'])
        out = subprocess.check_output(
            ['git', 'ls-files'], universal_newlines=True)
        assert out == textwrap.dedent("""\
            setup/.setuptools-odoo-make-default-ignore
            setup/README
        """)


if __name__ == '__main__':
    unittest.main()
