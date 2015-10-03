# -*- coding: utf-8 -*-
# © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

""" An odoo startup script that discovers addons in the odoo_addons namespace

Since it's not possible to make openerp.addons a namespace package
because openerp/__init__.py contains code, we use a pseudo-package named
odoo_addons for the sole purpose of discovering addons installed with
setuptools in that namespace. odoo_addons is not intended to be imported
as the Odoo import hook will make sure all addons can be imported from
openerp.addons.

See https://pythonhosted.org/setuptools/pkg_resources.html for more
information about namespace packages.

See https://github.com/odoo/odoo/pull/8758 to follow progress with making
openerp.addons a namespace package, which will hopefully make this monkey
patch obsolete in the future.
"""

import os

import openerp


initialize_sys_path_orig = openerp.modules.module.initialize_sys_path


def initialize_sys_path_odoo_addons():
    """ Monkey patch Odoo to discover addons from the odoo_addons namespace """
    initialize_sys_path_orig()

    ad_paths = openerp.modules.module.ad_paths

    try:
        for ad in __import__('odoo_addons').__path__:
            ad = os.path.abspath(ad)
            if ad not in ad_paths:
                ad_paths.append(ad)
    except ImportError:
        # odoo_addons is not provided by any distribution
        pass


openerp.modules.module.initialize_sys_path = initialize_sys_path_odoo_addons


def main():
    openerp.cli.main()


if __name__ == "__main__":
    main()
