# -*- coding: utf-8 -*-
# Copyright © 2015-2018 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)
""" List of Odoo official addons which are not released as individual packages.
They are therefore considered as installed as soon as the 'odoo' dependency
is satisfied. """

from pkg_resources import resource_string


def _addons(suffix):
    b = resource_string('setuptools_odoo', 'addons-%s.txt' % suffix)
    return set(b.decode('ascii').split())


openerp7 = _addons('7c')

odoo8 = _addons('8c')

odoo9c = _addons('9c')
odoo9e = _addons('9e')
odoo9 = odoo9c | odoo9e

odoo10c = _addons('10c')
odoo10e = _addons('10e')
odoo10 = odoo10c | odoo10e

odoo11c = _addons('11c')
odoo11e = _addons('11e')
odoo11 = odoo11c | odoo11e

odoo12c = _addons('12c')
odoo12e = _addons('12e')
odoo12 = odoo12c | odoo12e
