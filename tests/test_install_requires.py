# -*- coding: utf-8 -*-
# Copyright © 2015-2018 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)
import os
import unittest

import setuptools_odoo

from . import DATA_DIR


class TestInstallRequires(unittest.TestCase):
    """ Test the install_requires... public api """

    def test_addons_dir(self):
        r = setuptools_odoo.get_install_requires_odoo_addons(DATA_DIR)
        self.assertEquals(set(r), set([
            'astropy',
            # we have a mix of addons version, so two versions of Odoo
            # are pulled here (not realistic but good enough for a test)
            'odoo>=12.0a,<12.1dev',
            'odoo>=11.0a,<11.1dev',
            'odoo>=10.0,<10.1dev',
            'odoo>=8.0a,<9.0a',
            'python-dateutil']))

    def test_addon1(self):
        addon_dir = os.path.join(DATA_DIR, 'addon1')
        r = setuptools_odoo.get_install_requires_odoo_addon(addon_dir)
        self.assertEquals(r, ['odoo>=8.0a,<9.0a'])

    def test_addon2(self):
        addon_dir = os.path.join(DATA_DIR, 'addon2')
        r = setuptools_odoo.get_install_requires_odoo_addon(addon_dir)
        self.assertEquals(r, ['odoo8-addon-addon1',
                              'odoo>=8.0a,<9.0a',
                              'python-dateutil'])


if __name__ == '__main__':
    unittest.main()
