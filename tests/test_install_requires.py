import os
import unittest

import setuptools_odoo


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestInstallRequires(unittest.TestCase):

    def test_addons_dir(self):
        r = setuptools_odoo.get_install_requires_odoo_addons(DATA_DIR)
        self.assertEquals(r, ['odoo>=8.0a,<9.0a',
                              'python-dateutil'])

    def test_addon1(self):
        addon_dir = os.path.join(DATA_DIR, 'addon1')
        r = setuptools_odoo.get_install_requires_odoo_addon(addon_dir)
        self.assertEquals(r, ['odoo>=8.0a,<9.0a'])

    def test_addon2(self):
        addon_dir = os.path.join(DATA_DIR, 'addon2')
        r = setuptools_odoo.get_install_requires_odoo_addon(addon_dir)
        self.assertEquals(r, ['odoo-addon-addon1>=8.0a,<9.0a',
                              'odoo>=8.0a,<9.0a',
                              'python-dateutil'])


if __name__ == '__main__':
    unittest.main()
