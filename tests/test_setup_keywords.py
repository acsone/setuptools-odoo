# -*- coding: utf-8 -*-
# © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)
import os
import shutil
import subprocess
import unittest

from . import DATA_DIR


class TestSetupKeywords(unittest.TestCase):
    """ test the new setup() keywords """

    def test_odoo_addon1(self):
        addon1_dir = os.path.join(DATA_DIR, 'setup_reusable_addons', 'addon1')
        subprocess.check_call(['python', 'setup.py', 'egg_info'],
                              cwd=addon1_dir)
        shutil.rmtree(os.path.join(addon1_dir, 'odoo_addon_addon1.egg-info'))

    def test_odoo_addon2(self):
        addon2_dir = os.path.join(DATA_DIR, 'setup_reusable_addons', 'addon2')
        subprocess.check_call(['python', 'setup.py', 'egg_info'],
                              cwd=addon2_dir)
        shutil.rmtree(os.path.join(addon2_dir, 'odoo_addon_addon2.egg-info'))

    def test_custom_project(self):
        project_dir = os.path.join(DATA_DIR, 'setup_custom_project')
        subprocess.check_call(['python', 'setup.py', 'egg_info'],
                              cwd=project_dir)
        shutil.rmtree(os.path.join(project_dir, 'test_custom_project.egg-info'))


if __name__ == '__main__':
    unittest.main()
