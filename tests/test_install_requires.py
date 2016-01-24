# -*- coding: utf-8 -*-
# © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)
import os
import unittest

import setuptools_odoo

from . import DATA_DIR


class TestInstallRequires(unittest.TestCase):
    """ Test the install_requires... public api """

    def test_addons_dir(self):
        r = setuptools_odoo.get_install_requires_odoo_addons(DATA_DIR)
        self.assertEquals(r, ['astropy',
                              'odoo>=8.0a,<9.0a',
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
