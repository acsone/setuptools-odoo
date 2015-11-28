# -*- coding: utf-8 -*-
# © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import warnings

from .core import (
    prepare_odoo_addon,
    prepare_odoo_addons,
)


def _set_dist_keywords(dist, setup_keywords):
    # got this trick from pbr
    for key, val in setup_keywords.items():
        if hasattr(dist.metadata, 'set_' + key):
            getattr(dist.metadata, 'set_' + key)(val)
        elif hasattr(dist.metadata, key):
            setattr(dist.metadata, key, val)
        elif hasattr(dist, key):
            setattr(dist, key, val)
        else:
            msg = 'Unknown distribution option: %s' % repr(key)
            warnings.warn(msg)


def odoo_addon(dist, attr, value):
    setup_keywords = prepare_odoo_addon()
    _set_dist_keywords(dist, setup_keywords)


def odoo_addons(dist, attr, value):
    setup_keywords = prepare_odoo_addons()
    _set_dist_keywords(dist, setup_keywords)
