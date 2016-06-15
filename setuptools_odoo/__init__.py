# -*- coding: utf-8 -*-
# Copyright © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)


from .core import (
    prepare_odoo_addon,
    prepare_odoo_addons,
    get_install_requires_odoo_addon,
    get_install_requires_odoo_addons,
    make_pkg_name,
    make_pkg_requirement,
)


__all__ = [
    prepare_odoo_addon.__name__,
    prepare_odoo_addons.__name__,
    get_install_requires_odoo_addon.__name__,
    get_install_requires_odoo_addons.__name__,
    make_pkg_name.__name__,
    make_pkg_requirement.__name__,
]
