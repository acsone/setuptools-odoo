# -*- coding: utf-8 -*-
# Copyright © 2015-2018 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import ast
import os

MANIFEST_NAMES = ("__manifest__.py", "__openerp__.py", "__terp__.py")


class NoManifestFound(Exception):
    pass


def get_manifest_path(addon_dir):
    for manifest_name in MANIFEST_NAMES:
        manifest_path = os.path.join(addon_dir, manifest_name)
        if os.path.isfile(manifest_path):
            return manifest_path


def parse_manifest(s):
    return ast.literal_eval(s)


def read_manifest(addon_dir):
    manifest_path = get_manifest_path(addon_dir)
    if not manifest_path:
        raise NoManifestFound("no Odoo manifest found in %s" % addon_dir)
    with open(manifest_path) as mf:
        return parse_manifest(mf.read())


def is_installable_addon(addon_dir, unless_auto_installable=False):
    try:
        manifest = read_manifest(addon_dir)
        r = manifest.get("installable", True)
        if unless_auto_installable:
            r = r and not manifest.get("auto_install", False)
        return r
    except Exception:
        return False
