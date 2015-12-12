# -*- coding: utf-8 -*-
# © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import ast
import os
from distutils.core import DistutilsSetupError


def get_manifest_path(addon_dir):
    for manifest_name in ('__odoo__.py', '__openerp__.py', '__terp__.py'):
        manifest_path = os.path.join(addon_dir, manifest_name)
        if os.path.isfile(manifest_path):
            return manifest_path


def read_manifest(addon_dir):
    manifest_path = get_manifest_path(addon_dir)
    if not manifest_path:
        raise DistutilsSetupError("no Odoo manifest found in %s" % addon_dir)
    return ast.literal_eval(open(manifest_path).read())


def is_installable_addon(addon_dir):
    try:
        manifest = read_manifest(addon_dir)
        return manifest.get('installable', True)
    except:
        return False
