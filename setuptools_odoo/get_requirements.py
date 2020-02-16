# -*- coding: utf-8 -*-
# Copyright © 2020 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

from __future__ import print_function

import argparse
import ast
import os
import re
import sys

from .core import get_addon_metadata
from .manifest import is_installable_addon

# ignore odoo and odoo addons dependencies
EXTERNAL_REQ_RE = re.compile("^(odoo[^A-Za-z0-9-_]|odoo[0-9]*-addon-)")


def _get_odoo_addon_keyword(setup_py_path):
    """Get the value of the odoo_addon keyword argument in a setup.py file """
    with open(setup_py_path) as f:
        parsed = ast.parse(f.read())
        for node in ast.walk(parsed):
            if not isinstance(node, ast.Call) or node.func.attr != "setup":
                continue
            for kw in node.keywords:
                if kw.arg != "odoo_addon":
                    continue
                return ast.literal_eval(kw.value)
    return None


def get_metadata_overrides_from_setup_dir(addons_dir, addon_name, setup_dir="setup"):
    """Return a dictionary of metadata override keys, suitable for passing
    as kwargs to get_addon_metadata()."""
    overrides = {}
    setup_py_path = os.path.join(addons_dir, setup_dir, addon_name, "setup.py")
    if os.path.exists(setup_py_path):
        odoo_addon_keyword = _get_odoo_addon_keyword(setup_py_path)
        if isinstance(odoo_addon_keyword, dict):
            overrides = odoo_addon_keyword
    return overrides


def get_requirements(
    addons_dir, get_metadata_overrides=get_metadata_overrides_from_setup_dir
):
    requirements = set()
    for addon_name in os.listdir(addons_dir):
        addon_dir = os.path.join(addons_dir, addon_name)
        if not is_installable_addon(addon_dir):
            continue
        overrides = get_metadata_overrides(addons_dir, addon_name)
        metadata = get_addon_metadata(addon_dir, **overrides)
        for install_require in metadata.get_all("Requires-Dist"):
            if EXTERNAL_REQ_RE.match(install_require):
                continue
            requirements.add(install_require)
    return sorted(requirements)


def main(args=None):
    parser = argparse.ArgumentParser(
        description=(
            "Print external python dependencies for all addons in an "
            "Odoo addons directory."
        )
    )
    parser.add_argument("--addons-dir", "-d", default=".")
    parser.add_argument("--output", "-o", default="-")
    args = parser.parse_args(args)
    requirements = "\n".join(get_requirements(args.addons_dir))
    if args.output == "-":
        print(requirements)
    else:
        with open(args.output, "w") as f:
            print(requirements, file=f)


if __name__ == "__main__":
    main(sys.argv[1:])
