# -*- coding: utf-8 -*-
# Copyright © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import argparse
import datetime
import logging
import os
import re
import subprocess

from .core import is_installable_addon, _get_version, make_pkg_requirement
from .manifest import read_manifest

_logger = logging.getLogger(__name__)

SETUP_PY = """import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={odoo_addon},
)
"""

SETUP_PY_METAPACKAGE = """
import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo{odoo_version}-addons-{name}",
    description="Meta package for {name} Odoo addons",
    version=version,
    install_requires={install_requires},
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
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

def make_default_meta_package(addons_dir, name):
    meta_install_requires = []
    new_version = False
    odoo_versions = set()
    version_date = datetime.date.today().strftime('%Y%m%d')
    metapackage_dir = os.path.join(addons_dir, 'setup', '_metapackage')
    meta_package_setup_file = os.path.join(metapackage_dir, 'setup.py')
    version_setup_file = os.path.join(metapackage_dir, 'VERSION.txt')
    original_file_content = None

    for addon_name in os.listdir(addons_dir):
        addon_dir = os.path.join(addons_dir, addon_name)
        if not is_installable_addon(addon_dir):
            continue
        meta_install_requires.append(make_pkg_requirement(addon_dir))
        manifest = read_manifest(addon_dir)
        version, odoo_version_info = _get_version(
            addon_dir, manifest, git_post_version=False)
        odoo_version = version.split('.')[0]
        odoo_versions.add(odoo_version)
    if len(odoo_versions) == 0:
        _logger.warning(
            "Unable to determine the Odoo version in %s." % (addons_dir,))
        return
    if len(odoo_versions) > 1:
        raise RuntimeError("not all addon are for the same "
                           "Odoo version: %s" % (odoo_versions,))
    odoo_version = list(odoo_versions)[0]
    install_requires_str = '[\n%s%s]' % (
        ''.join([
            ' '*8 + '\'' + install_require + '\',\n'
            for install_require in sorted(meta_install_requires)
        ]),
        ' '*4,
    )

    setup_py = SETUP_PY_METAPACKAGE.format(
        name=name,
        odoo_version=list(odoo_versions)[0],
        date=version_date,
        install_requires=install_requires_str,
    )

    if not os.path.exists(metapackage_dir):
        os.mkdir(metapackage_dir)

    if os.path.exists(meta_package_setup_file):
        with open(meta_package_setup_file, 'r') as f:
            original_file_content = f.read()

    if not os.path.exists(version_setup_file):
        with open(version_setup_file, 'w') as f:
            pass

    if original_file_content is None or original_file_content != setup_py:
        with open(version_setup_file, 'r') as f:
            old_version = f.read().strip()
            new_version = get_next_version(
                odoo_version, version_date, old_version)

    if new_version:
        with open(version_setup_file, 'w') as f:
            f.write(new_version)

    with open(meta_package_setup_file, 'w') as f:
        f.write(setup_py)


def get_next_version(odoo_version, version_date, old_version=None):
    new_version = "%s.0.%s" % (odoo_version, version_date)
    use_counter = False
    index = 0
    if old_version:
        old_date = re.findall(
            r'[0-9]{8}', old_version)[0]
        old_index = re.sub(
            r'' + odoo_version + '.0.[0-9]{8}(.)?', '', old_version)
        if old_index:
            index = int(old_index)
        if old_date == version_date:
            use_counter = True
        if use_counter:
            index += 1
            new_version = '%s.%s' % (new_version, index)
    return new_version


def make_default_setup_commit_files(addons_dir):
    subprocess.check_call(['git', 'add', 'setup'], cwd=addons_dir)
    commit_needed = subprocess.call([
        'git', 'diff', '--quiet', '--cached',
        '--exit-code', 'setup'
    ], cwd=addons_dir) != 0
    if commit_needed:
        subprocess.check_call([
            'git', 'commit', '-m', '[ADD] setup.py',
        ], cwd=addons_dir)


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
    parser.add_argument(
        '--metapackage', '-m',
        help="Create a metapackage using the given name.")
    parser.add_argument(
        '--commit',
        action='store_true', help="Commit the changes if there is any.")
    args = parser.parse_args(args)
    make_default_setup_addons_dir(args.addons_dir, args.force,
                                  args.odoo_version_override)
    if args.metapackage:
        make_default_meta_package(args.addons_dir, args.metapackage)

    if args.commit:
        make_default_setup_commit_files(args.addons_dir)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
