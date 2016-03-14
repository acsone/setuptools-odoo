# -*- coding: utf-8 -*-
# © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import argparse
import os


from .core import ADDONS_NAMESPACE, is_installable_addon

SETUP_PY = """import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon=True,
)
"""

INIT_PY = """__import__('pkg_resources').declare_namespace(__name__)
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


def make_default_setup_addon(addon_setup_dir, addon_dir, force):
    addon_name = os.path.basename(os.path.realpath(addon_dir))
    setup_path = os.path.join(addon_setup_dir, 'setup.py')
    if not os.path.exists(setup_path) or force:
        with open(setup_path, 'w') as f:
            f.write(SETUP_PY.format(addon_name=addon_name))
    odoo_addons_path = os.path.join(addon_setup_dir, ADDONS_NAMESPACE)
    if not os.path.exists(odoo_addons_path):
        os.mkdir(odoo_addons_path)
    init_path = os.path.join(odoo_addons_path, '__init__.py')
    if not os.path.exists(init_path) or force:
        with open(init_path, 'w') as f:
            f.write(INIT_PY)
    link_path = os.path.join(odoo_addons_path, addon_name)
    # symlink to the main addon directory so we have a canonical structure:
    # odoo_addons/addon_name/...
    if os.path.exists(link_path) and force:
        os.remove(link_path)
    if not os.path.exists(link_path):
        os.symlink(os.path.relpath(addon_dir, odoo_addons_path), link_path)


def make_default_setup_addons_dir(addons_dir, force):
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
        make_default_setup_addon(addon_setup_dir, addon_dir, force)


def main(args=None):
    parser = argparse.ArgumentParser(
        description='Generate default setup.py for all addons in an '
                    'Odoo addons directory'
    )
    parser.add_argument('--addons-dir', '-d', required=True)
    parser.add_argument('--force', '-f', action='store_true')
    args = parser.parse_args(args)
    make_default_setup_addons_dir(args.addons_dir, args.force)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
