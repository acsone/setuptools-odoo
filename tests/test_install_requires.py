# -*- coding: utf-8 -*-
# Copyright © 2015-2018 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)
import os
import unittest

from setuptools_odoo.core import (
    ODOO_VERSION_INFO,
    _get_install_requires,
    get_install_requires_odoo_addon,
    get_install_requires_odoo_addons,
)

from . import DATA_DIR


class TestInstallRequires(unittest.TestCase):
    """Test the install_requires... public api"""

    def test_addons_dir(self):
        r = get_install_requires_odoo_addons(DATA_DIR)
        self.assertEqual(
            set(r),
            {
                "astropy",
                # we have a mix of addons version, so two versions of Odoo
                # are pulled here (not realistic but good enough for a test)
                "odoo>=12.0a,<12.1dev",
                "odoo>=11.0a,<11.1dev",
                "odoo>=10.0,<10.1dev",
                "odoo>=8.0a,<9.0a",
                "python-dateutil",
                "odoo>=15.0a,<15.1dev",
                "odoo-addon-another_addon>=15.0dev,<15.1dev",
            },
        )

    def test_addon1(self):
        addon_dir = os.path.join(DATA_DIR, "addon1")
        r = get_install_requires_odoo_addon(addon_dir)
        self.assertEqual(r, ["odoo>=8.0a,<9.0a"])

    def test_addon2(self):
        addon_dir = os.path.join(DATA_DIR, "addon2")
        r = get_install_requires_odoo_addon(addon_dir)
        self.assertEqual(
            r, ["odoo8-addon-addon1", "odoo>=8.0a,<9.0a", "python-dateutil"]
        )


def test__get_install_requires_one2many_override():
    """Test external dependencies override one to many"""
    manifest = {
        "external_dependencies": {
            "python": [
                "mpld3",
            ],
        }
    }
    external_dependencies_override = {
        "python": {
            "mpld3": [
                "mpld3==0.3",
                "matplotlib==3.0.3; python_version < '3.7'",
                "matplotlib==3.4.1; python_version >= '3.7'",
            ],
        },
    }
    install_requires = _get_install_requires(
        ODOO_VERSION_INFO["12.0"],
        manifest,
        no_depends=None,
        depends_override=None,
        external_dependencies_override=external_dependencies_override,
    )
    assert install_requires == [
        "matplotlib==3.0.3; python_version < '3.7'",
        "matplotlib==3.4.1; python_version >= '3.7'",
        "mpld3==0.3",
        "odoo>=12.0a,<12.1dev",
    ]


if __name__ == "__main__":
    unittest.main()
