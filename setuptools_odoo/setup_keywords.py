# -*- coding: utf-8 -*-
# Copyright © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import warnings

from .core import (
    prepare_odoo_addon,
    prepare_odoo_addons,
)


def _set_dist_keyword(dist, key, val):
    v = getattr(dist, key)
    if v is None:
        # not set in setup.py, use what we get from __openerp__.py
        setattr(dist, key, val)
    elif isinstance(v, list):
        # list set in setup.py, extend with what we get from __openerp__.py
        # (for install_requires, classifiers, etc)
        assert isinstance(val, list)
        for item in val:
            if item not in v:
                v.append(item)


def _set_dist_keywords(dist, setup_keywords):
    # got this trick from pbr
    for key, val in setup_keywords.items():
        if hasattr(dist.metadata, key):
            _set_dist_keyword(dist.metadata, key, val)
        elif hasattr(dist, key):
            _set_dist_keyword(dist, key, val)
        else:
            msg = 'Unknown distribution option: %s' % repr(key)
            warnings.warn(msg)


def _parse_options(value):
    depends_override = {}
    external_dependencies_override = {}
    odoo_version_override = None
    if isinstance(value, dict):
        depends_override = \
            value.get('depends_override', {})
        external_dependencies_override = \
            value.get('external_dependencies_override', {})
        odoo_version_override = \
            value.get('odoo_version_override')
    return (
        depends_override,
        external_dependencies_override,
        odoo_version_override,
    )


def odoo_addon(dist, attr, value):
    depends_override, external_dependencies_override, odoo_version_override = \
        _parse_options(value)
    setup_keywords = prepare_odoo_addon(
        depends_override=depends_override,
        external_dependencies_override=external_dependencies_override,
        odoo_version_override=odoo_version_override,
    )
    _set_dist_keywords(dist, setup_keywords)


def odoo_addons(dist, attr, value):
    depends_override, external_dependencies_override, odoo_version_override = \
        _parse_options(value)
    setup_keywords = prepare_odoo_addons(
        depends_override=depends_override,
        external_dependencies_override=external_dependencies_override,
        odoo_version_override=odoo_version_override,
    )
    _set_dist_keywords(dist, setup_keywords)
