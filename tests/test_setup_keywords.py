# -*- coding: utf-8 -*-
# Copyright © 2015-2018 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import glob
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from zipfile import ZipFile

import pkg_resources

from . import DATA_DIR


class TestSetupKeywords(unittest.TestCase):
    """ test the new setup() keywords (odoo_addon, odoo_addons) """

    def test_odoo_addon1(self):
        addon1_dir = os.path.join(DATA_DIR, 'setup_reusable_addons', 'addon1')
        subprocess.check_call([sys.executable, 'setup.py', 'egg_info'],
                              cwd=addon1_dir)
        egg_info_dir = os.path.join(addon1_dir,
                                    'odoo8_addon_addon1.egg-info')
        assert os.path.isdir(egg_info_dir)
        try:
            dist = next(pkg_resources.find_distributions(addon1_dir))
            self.assertEquals(dist.key, 'odoo8-addon-addon1')
            self.assertEquals(dist.requires(),
                              [pkg_resources.Requirement.parse(r) for r in
                               ['odoo>=8.0a,<9.0a']])
            self.assertTrue(dist.has_metadata('not-zip-safe'))
            self.assertEquals(dist.version, "8.0.1.0.0.99.dev2")
        finally:
            shutil.rmtree(egg_info_dir)

    def test_odoo_addon1_sdist(self):
        addon1_dir = os.path.join(DATA_DIR, 'setup_reusable_addons', 'addon1')
        dist_dir = tempfile.mkdtemp()
        assert os.path.isdir(dist_dir)
        try:
            subprocess.check_call([
                sys.executable, 'setup.py', 'sdist', '-d', dist_dir,
            ], cwd=addon1_dir)
            sdist_file = os.path.join(
                dist_dir,
                'odoo8-addon-addon1-8.0.1.0.0.99.dev2.tar.gz')
            assert os.path.isfile(sdist_file)
            # dist from the tar file, must produce an identical tar file
            with tarfile.open(sdist_file, 'r') as tf:
                tar_dir = tempfile.mkdtemp()
                try:
                    tar_setup_dir = os.path.join(
                        tar_dir, 'odoo8-addon-addon1-8.0.1.0.0.99.dev2')
                    tf.extractall(tar_dir)
                    subprocess.check_call([
                        sys.executable, 'setup.py', 'sdist',
                    ], cwd=tar_setup_dir)
                    sdist_file2 = os.path.join(
                        tar_setup_dir, 'dist',
                        'odoo8-addon-addon1-8.0.1.0.0.99.dev2.tar.gz')
                    assert os.path.isfile(sdist_file2)
                    with tarfile.open(sdist_file2, 'r') as tf2:
                        assert sorted(tf.getnames()) == sorted(tf2.getnames())
                finally:
                    shutil.rmtree(tar_dir)
        finally:
            shutil.rmtree(dist_dir)

    def test_odoo_addon2(self):
        addon2_dir = os.path.join(DATA_DIR, 'setup_reusable_addons', 'addon2')
        subprocess.check_call([sys.executable, 'setup.py', 'egg_info'],
                              cwd=addon2_dir)
        egg_info_dir = os.path.join(addon2_dir,
                                    'odoo8_addon_addon2.egg-info')
        assert os.path.isdir(egg_info_dir)
        try:
            dist = next(pkg_resources.find_distributions(addon2_dir))
            self.assertEquals(dist.key, 'odoo8-addon-addon2')
            self.assertEquals(dist.requires(),
                              [pkg_resources.Requirement.parse(r) for r in
                               ['odoo8-addon-addon1',
                                'odoo>=8.0a,<9.0a',
                                'python-dateutil']])
            self.assertTrue(dist.has_metadata('not-zip-safe'))
            self.assertEquals(dist.version, "8.0.1.0.1")
        finally:
            shutil.rmtree(egg_info_dir)

    def test_odoo_addon4(self):
        addon4_dir = os.path.join(DATA_DIR, 'setup_reusable_addons', 'addon4')
        subprocess.check_call([sys.executable, 'setup.py', 'egg_info'],
                              cwd=addon4_dir)
        egg_info_dir = os.path.join(addon4_dir,
                                    'odoo8_addon_addon4.egg-info')
        assert os.path.isdir(egg_info_dir)
        try:
            dist = next(pkg_resources.find_distributions(addon4_dir))
            self.assertEquals(dist.key, 'odoo8-addon-addon4')
            self.assertEquals(dist.requires(),
                              [pkg_resources.Requirement.parse(r) for r in
                               ['astropy>=1.0',
                                'odoo8-addon-addon1>=8.0.3.0.0',
                                'odoo>=8.0a,<9.0a',
                                'python-dateutil']])
            self.assertTrue(dist.has_metadata('not-zip-safe'))
            self.assertEquals(dist.version, "8.0.2.0.0")
        finally:
            shutil.rmtree(egg_info_dir)

    def test_odoo_addon5(self):
        addon5_dir = os.path.join(DATA_DIR, 'setup_reusable_addons', 'addon5')
        subprocess.check_call([sys.executable, 'setup.py', 'egg_info'],
                              cwd=addon5_dir)
        egg_info_dir = os.path.join(addon5_dir,
                                    'odoo8_addon_addon5.egg-info')
        assert os.path.isdir(egg_info_dir)
        try:
            dist = next(pkg_resources.find_distributions(addon5_dir))
            self.assertEquals(dist.key, 'odoo8-addon-addon5')
        finally:
            shutil.rmtree(egg_info_dir)

    def test_odoo_addon5_wheel(self):
        addon5_dir = os.path.join(DATA_DIR, 'setup_reusable_addons', 'addon5')
        # add a file that is not under git control
        notingit_fname = os.path.join(
            addon5_dir, 'odoo_addons', 'addon5', 'data', 'notingit.xml')
        with open(notingit_fname, 'w') as f:
            f.write('<stuff/>')
        self.assertTrue(os.path.isfile(notingit_fname))
        try:
            bdist_dir = tempfile.mkdtemp()
            assert os.path.isdir(bdist_dir)
            try:
                dist_dir = tempfile.mkdtemp()
                assert os.path.isdir(dist_dir)
                try:
                    subprocess.check_call([sys.executable,
                                           'setup.py', 'bdist_wheel',
                                           '-b', bdist_dir, '-d', dist_dir],
                                          cwd=addon5_dir)
                    wheel_fname = glob.glob(os.path.join(dist_dir, '*.whl'))[0]
                    with ZipFile(wheel_fname) as zf:
                        namelist = zf.namelist()
                        assert 'odoo_addons/addon5/__openerp__.py' \
                            in namelist
                        # some non python file was included because #
                        # it is under git control
                        assert 'odoo_addons/addon5/data/somedata.xml' \
                            in namelist
                        # this file is not under git control,
                        # so its not in the wheel
                        assert 'odoo_addons/addon5/data/notingit.xml' \
                            not in namelist
                finally:
                    shutil.rmtree(dist_dir)
                    shutil.rmtree(os.path.join(
                        addon5_dir, 'build'))
                    shutil.rmtree(os.path.join(
                        addon5_dir, 'odoo8_addon_addon5.egg-info'))
            finally:
                if os.path.isdir(bdist_dir):
                    shutil.rmtree(bdist_dir)
        finally:
            os.unlink(notingit_fname)

    def test_custom_project(self):
        project_dir = os.path.join(DATA_DIR, 'setup_custom_project')
        subprocess.check_call([sys.executable, 'setup.py', 'egg_info'],
                              cwd=project_dir)
        egg_info_dir = os.path.join(project_dir,
                                    'test_custom_project.egg-info')
        assert os.path.isdir(egg_info_dir)
        dist = next(pkg_resources.find_distributions(project_dir))
        self.assertEquals(dist.requires(),
                          [pkg_resources.Requirement.parse(r) for r in
                           ['pyflakes',
                            'odoo>=8.0a,<9.0a',
                            'python-dateutil']])
        self.assertFalse(dist.has_metadata('not-zip-safe'))
        shutil.rmtree(egg_info_dir)


if __name__ == '__main__':
    unittest.main()
