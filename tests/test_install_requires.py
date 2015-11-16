import os
import unittest

import setuptools_odoo


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestInstallRequires(unittest.TestCase):

    def test_addons_dir(self):
        r = setuptools_odoo.get_install_requires_addons_dir(DATA_DIR)
        self.assertEquals(r, ['odoo>=8,<9',
                              'python-dateutil'])

    def test_addon1(self):
        addon_dir = os.path.join(DATA_DIR, 'addon1')
        r = setuptools_odoo.get_install_requires(addon_dir)
        self.assertEquals(r, ['odoo>=8,<9'])

    def test_addon2(self):
        addon_dir = os.path.join(DATA_DIR, 'addon2')
        r = setuptools_odoo.get_install_requires(addon_dir)
        self.assertEquals(r, ['odoo-addon-addon1>=8,<9',
                              'odoo>=8,<9',
                              'python-dateutil'])


if __name__ == '__main__':
    unittest.main()
