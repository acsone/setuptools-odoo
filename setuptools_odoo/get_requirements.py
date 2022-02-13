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
from .git_postversion import STRATEGY_NONE
from .manifest import is_installable_addon

# ignore odoo and odoo addons dependencies
ODOO_REQ_RE = re.compile("^(odoo|odoo[0-9]*[-_]addon[-_].*)$", re.IGNORECASE)
REQ_NAME_RE = re.compile("^[A-Za-z0-9-._]+")


def _canonicalize(requirement):
    return requirement.lower().replace("-", "_")


def _get_req_name(requirement):
    return _canonicalize(REQ_NAME_RE.match(requirement).group(0))


def _get_odoo_addon_keyword(setup_py_path):
    """Get the value of the odoo_addon keyword argument in a setup.py file"""
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


def _get_metadata_overrides_from_setup_dir(addons_dir, addon_name, setup_dir="setup"):
    """Return a dictionary of metadata override keys, suitable for passing
    as kwargs to get_addon_metadata()."""
    overrides = {}
    setup_py_path = os.path.join(addons_dir, setup_dir, addon_name, "setup.py")
    if os.path.exists(setup_py_path):
        odoo_addon_keyword = _get_odoo_addon_keyword(setup_py_path)
        if isinstance(odoo_addon_keyword, dict):
            overrides = odoo_addon_keyword
    return overrides


def _get_requirements(
    addons_dir,
    get_metadata_overrides=_get_metadata_overrides_from_setup_dir,
    include_addons=False,
):
    requirements = set()
    local_addons = set()
    for addon_name in os.listdir(addons_dir):
        addon_dir = os.path.join(addons_dir, addon_name)
        if not is_installable_addon(addon_dir):
            continue
        # TODO this is a hack and we should run proper metadata preparation instead,
        #      using build.utils.project_wheel_metadata()
        overrides = get_metadata_overrides(addons_dir, addon_name)
        # We don't care about the version here, so improve performance
        # by skipping git post version lookup.
        overrides["post_version_strategy_override"] = STRATEGY_NONE
        metadata = get_addon_metadata(addon_dir, **overrides)
        local_addons.add(_canonicalize(metadata.get("Name")))
        for install_require in metadata.get_all("Requires-Dist"):
            if not include_addons and ODOO_REQ_RE.match(_get_req_name(install_require)):
                continue
            requirements.add(install_require)
    if include_addons:
        # Exclude local addons as they cannot be considered to be dependencies
        # of addons in addons_dir.
        requirements = {r for r in requirements if _get_req_name(r) not in local_addons}
    return sorted(requirements, key=lambda s: s.lower())


def _render(requirements, header, fp):
    if header:
        print(header, file=fp)
    for requirement in requirements:
        print(requirement, file=fp)


def main(args=None):
    parser = argparse.ArgumentParser(
        description=(
            "Print external python dependencies for all addons in an "
            "Odoo addons directory. If dependencies overrides are declared "
            "in setup/{addon}/setup.py, they are honored in the output. "
        )
    )
    parser.add_argument(
        "--addons-dir",
        "-d",
        default=".",
        help="addons directory (default: .)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="-",
        help="output file (default: stdout)",
    )
    parser.add_argument(
        "--header",
        help="output file header",
    )
    parser.add_argument(
        "--include-addons",
        action="store_true",
        help=(
            "Include addons and odoo requirements in addition to "
            "python external dependencies (default: false)"
        ),
    )
    args = parser.parse_args(args)
    requirements = _get_requirements(
        args.addons_dir, include_addons=args.include_addons
    )
    if args.output == "-":
        _render(requirements, args.header, sys.stdout)
    else:
        if os.path.exists(args.output) or requirements:
            with open(args.output, "w") as fp:
                _render(requirements, args.header, fp)


if __name__ == "__main__":
    main(sys.argv[1:])
