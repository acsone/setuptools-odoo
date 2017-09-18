# -*- coding: utf-8 -*-
# Copyright © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import argparse
import os


from .core import is_installable_addon, _get_version
from .manifest import read_manifest

SETUP_PY = """import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={odoo_addon},
)
"""

SETUP_CFG_UNIVERSAL = """[bdist_wheel]
universal=1
"""

NS_INIT_PY = """__import__('pkg_resources').declare_namespace(__name__)
"""

README = """To learn more about this directory, please visit
https://pypi.python.org/pypi/setuptools-odoo
"""

IGNORE = """# addons listed in this file are ignored by
# setuptools-odoo-make-default (one addon per line)
"""

IGNORE_FILENAME = '.setuptools-odoo-make-default-ignore'


def _load_ignore_file(ignore_path):
    ignore = set()
    if os.path.exists(ignore_path):
        for line in open(ignore_path):
            if line.startswith('#'):
                continue
            ignore.add(line.strip())
    return ignore


def make_ns_pkg_dirs(root, pkgs, force, with_ns_init_py):
    for pkg in pkgs.split('.'):
        root = os.path.join(root, pkg)
        if not os.path.isdir(root):
            os.mkdir(root)
        init_path = os.path.join(root, '__init__.py')
        if with_ns_init_py:
            if not os.path.exists(init_path) or force:
                with open(init_path, 'w') as f:
                    f.write(NS_INIT_PY)
        else:
            if os.path.exists(init_path):
                os.remove(init_path)
    return root


def make_default_setup_addon(addon_setup_dir, addon_dir, force,
                             odoo_version_override):
    manifest = read_manifest(addon_dir)
    _, odoo_version_info = _get_version(addon_dir,
                                        manifest,
                                        odoo_version_override,
                                        git_post_version=False)
    addon_name = os.path.basename(os.path.realpath(addon_dir))
    setup_path = os.path.join(addon_setup_dir, 'setup.py')
    odoo_addon = 'True'
    if odoo_version_override:
        odoo_addon = "{'odoo_version_override': '%s'}" % odoo_version_override
    if not os.path.exists(setup_path) or force:
        with open(setup_path, 'w') as f:
            f.write(SETUP_PY.format(odoo_addon=odoo_addon))
    odoo_addons_path = make_ns_pkg_dirs(
        addon_setup_dir, odoo_version_info['addons_ns'], force,
        with_ns_init_py=bool(odoo_version_info['namespace_packages']))
    link_path = os.path.join(odoo_addons_path, addon_name)
    # symlink to the main addon directory so we have a canonical structure:
    # odoo_addons/addon_name/...
    if os.path.exists(link_path) and force:
        os.remove(link_path)
    if not os.path.exists(link_path):
        os.symlink(os.path.relpath(addon_dir, odoo_addons_path), link_path)
    # setup.cfg
    if odoo_version_info['universal_wheel']:
        setup_cfg_path = os.path.join(addon_setup_dir, 'setup.cfg')
        with open(setup_cfg_path, 'w') as f:
            f.write(SETUP_CFG_UNIVERSAL)


def make_default_setup_addons_dir(addons_dir, force,
                                  odoo_version_override):
    addons_setup_dir = os.path.join(addons_dir, 'setup')
    if not os.path.exists(addons_setup_dir):
        os.mkdir(addons_setup_dir)
    readme_path = os.path.join(addons_setup_dir, 'README')
    if not os.path.exists(readme_path):
        with open(readme_path, "w") as f:
            f.write(README)
    ignore_path = os.path.join(addons_setup_dir, IGNORE_FILENAME)
    if not os.path.exists(ignore_path):
        with open(ignore_path, "w") as f:
            f.write(IGNORE)
    ignore = _load_ignore_file(ignore_path)
    for addon_name in os.listdir(addons_dir):
        if addon_name in ignore:
            continue
        addon_dir = os.path.join(addons_dir, addon_name)
        if not is_installable_addon(addon_dir):
            continue
        addon_setup_dir = os.path.join(addons_setup_dir, addon_name)
        if not os.path.exists(addon_setup_dir):
            os.mkdir(addon_setup_dir)
        make_default_setup_addon(addon_setup_dir, addon_dir, force,
                                 odoo_version_override)


def main(args=None):
    parser = argparse.ArgumentParser(
        description='Generate default setup.py for all addons in an '
                    'Odoo addons directory'
    )
    parser.add_argument('--addons-dir', '-d', required=True)
    parser.add_argument('--force', '-f', action='store_true')
    parser.add_argument('--odoo-version-override',
                        help="Force Odoo version for situations where some "
                             "addons versions do not start with the odoo "
                             "version")
    args = parser.parse_args(args)
    make_default_setup_addons_dir(args.addons_dir, args.force,
                                  args.odoo_version_override)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
