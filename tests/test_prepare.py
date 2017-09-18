# -*- coding: utf-8 -*-
# Copyright © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)
import os
import unittest

from setuptools_odoo.core import (
    prepare_odoo_addon,
    prepare_odoo_addons,
    make_pkg_name,
    make_pkg_requirement,
    ODOO_VERSION_INFO,
)

from . import DATA_DIR, working_directory_keeper


class TestPrepare(unittest.TestCase):
    """ Test the prepare... public api """

    def test_make_pkg_name(self):
        pkg_name = make_pkg_name(ODOO_VERSION_INFO['8.0'], 'addon1')
        self.assertEquals(pkg_name, 'odoo8-addon-addon1')

    def test_make_pkg_requirement(self):
        addon_dir = os.path.join(DATA_DIR, 'addon1')
        requirement = make_pkg_requirement(addon_dir)
        self.assertEquals(requirement, 'odoo8-addon-addon1')

    def test_addon1(self):
        self.maxDiff = None
        addon_dir = os.path.join(DATA_DIR, 'setup_reusable_addons', 'addon1')
        with working_directory_keeper:
            os.chdir(addon_dir)
            keywords = prepare_odoo_addon()
            self.assertEquals(keywords, {
                'author': 'ACSONE SA/NV, Odoo Community Association (OCA)',
                'author_email': 'support@odoo-community.org',
                'classifiers': [
                    'Programming Language :: Python',
                    'Framework :: Odoo',
                    'License :: OSI Approved :: '
                    'GNU Affero General Public License v3',
                ],
                'description': 'addon 1 summary',
                'include_package_data': True,
                'install_requires': ['odoo>=8.0a,<9.0a'],
                'python_requires': '~=2.7',
                'license': 'AGPL-3',
                'long_description': 'addon 1 readme content\n',
                'name': 'odoo8-addon-addon1',
                'namespace_packages': ['odoo_addons'],
                'packages': ['odoo_addons'],
                'url': 'https://acsone.eu/',
                'version': '8.0.1.0.0.99.dev2',
                'zip_safe': False,
            })

    def test_addon2(self):
        addon_dir = os.path.join(DATA_DIR, 'setup_reusable_addons', 'addon2')
        with working_directory_keeper:
            os.chdir(addon_dir)
            keywords = prepare_odoo_addon()
            self.assertEquals(keywords, {
                'classifiers': [
                    'Programming Language :: Python',
                    'Framework :: Odoo',
                ],
                'description': 'addon 2 summary',
                'include_package_data': True,
                'install_requires': ['odoo8-addon-addon1',
                                     'odoo>=8.0a,<9.0a',
                                     'python-dateutil'],
                'python_requires': '~=2.7',
                'name': 'odoo8-addon-addon2',
                'namespace_packages': ['odoo_addons'],
                'packages': ['odoo_addons'],
                'version': '8.0.1.0.1',
                'zip_safe': False,
            })

    def test_addons_dir(self):
        addons_dir = os.path.join(DATA_DIR, 'setup_custom_project')
        with working_directory_keeper:
            os.chdir(addons_dir)
            keywords = prepare_odoo_addons()
            self.assertEquals(keywords, {
                'include_package_data': True,
                'install_requires': ['odoo>=8.0a,<9.0a',
                                     'python-dateutil'],
                'python_requires': '~=2.7',
                'namespace_packages': ['odoo_addons'],
                'packages': ['odoo_addons'],
                'zip_safe': False,
            })


if __name__ == '__main__':
    unittest.main()
