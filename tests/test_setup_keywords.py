# -*- coding: utf-8 -*-
# © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import os
import pkg_resources
import shutil
import subprocess
import sys
import unittest

from . import DATA_DIR


class TestSetupKeywords(unittest.TestCase):
    """ test the new setup() keywords (odoo_addon, odoo_addons) """

    def test_odoo_addon1(self):
        addon1_dir = os.path.join(DATA_DIR, 'setup_reusable_addons', 'addon1')
        subprocess.check_call([sys.executable, 'setup.py', 'egg_info'],
                              cwd=addon1_dir)
        egg_info_dir = os.path.join(addon1_dir,
                                    'odoo_addon_addon1.egg-info')
        assert os.path.isdir(egg_info_dir)
        try:
            dist = pkg_resources.find_distributions(addon1_dir).next()
            self.assertEquals(dist.key, 'odoo-addon-addon1')
            self.assertEquals(dist.requires(),
                              [pkg_resources.Requirement.parse(r) for r in
                               ['odoo>=8.0a,<9.0a']])
            self.assertTrue(dist.has_metadata('not-zip-safe'))
            self.assertEquals(dist.version, "8.0.1.0.0.99.dev1")
        finally:
            shutil.rmtree(egg_info_dir)

    def test_odoo_addon2(self):
        addon2_dir = os.path.join(DATA_DIR, 'setup_reusable_addons', 'addon2')
        subprocess.check_call([sys.executable, 'setup.py', 'egg_info'],
                              cwd=addon2_dir)
        egg_info_dir = os.path.join(addon2_dir,
                                    'odoo_addon_addon2.egg-info')
        assert os.path.isdir(egg_info_dir)
        try:
            dist = pkg_resources.find_distributions(addon2_dir).next()
            self.assertEquals(dist.key, 'odoo-addon-addon2')
            self.assertEquals(dist.requires(),
                              [pkg_resources.Requirement.parse(r) for r in
                               ['odoo-addon-addon1>=8.0a,<9.0a',
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
                                    'odoo_addon_addon4.egg-info')
        assert os.path.isdir(egg_info_dir)
        try:
            dist = pkg_resources.find_distributions(addon4_dir).next()
            self.assertEquals(dist.key, 'odoo-addon-addon4')
            self.assertEquals(dist.requires(),
                              [pkg_resources.Requirement.parse(r) for r in
                               ['astropy>=1.0',
                                'odoo-addon-addon1>=8.0.3.0.0,<9.0a',
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
                                    'odoo_addon_addon5.egg-info')
        assert os.path.isdir(egg_info_dir)
        try:
            dist = pkg_resources.find_distributions(addon5_dir).next()
            self.assertEquals(dist.key, 'odoo-addon-addon5')
        finally:
            shutil.rmtree(egg_info_dir)

    def test_custom_project(self):
        project_dir = os.path.join(DATA_DIR, 'setup_custom_project')
        subprocess.check_call([sys.executable, 'setup.py', 'egg_info'],
                              cwd=project_dir)
        egg_info_dir = os.path.join(project_dir,
                                    'test_custom_project.egg-info')
        assert os.path.isdir(egg_info_dir)
        dist = pkg_resources.find_distributions(project_dir).next()
        self.assertFalse(dist.has_metadata('not-zip-safe'))
        shutil.rmtree(egg_info_dir)


if __name__ == '__main__':
    unittest.main()
