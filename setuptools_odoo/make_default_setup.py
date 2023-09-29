# -*- coding: utf-8 -*-
# Copyright © 2015-2018 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys

from .core import _get_version, is_installable_addon, make_pkg_requirement
from .manifest import NoManifestFound, read_manifest

SETUP_PY = """\
import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={odoo_addon},
)
"""

METAPACKAGE_SETUP_DIR = "_metapackage"

SETUP_PY_METAPACKAGE = """\
import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="{pkg_name_pfx}s-{name}",
    description="Meta package for {name} Odoo addons",
    version=version,
    install_requires={install_requires},
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: {odoo_version}',
    ]
)
"""

SETUP_CFG_UNIVERSAL = """\
[bdist_wheel]
universal=1
"""

NS_INIT_PY = """\
__import__('pkg_resources').declare_namespace(__name__)
"""

README = """\
To learn more about this directory, please visit
https://pypi.python.org/pypi/setuptools-odoo
"""

IGNORE = """\
# addons listed in this file are ignored by
# setuptools-odoo-make-default (one addon per line)
"""

IGNORE_FILENAME = ".setuptools-odoo-make-default-ignore"


def _load_ignore_file(ignore_path):
    ignore = set()
    if os.path.exists(ignore_path):
        for line in open(ignore_path):
            if line.startswith("#"):
                continue
            ignore.add(line.strip())
    return ignore


def _odoo_version_to_series(odoo_version):
    return int(float(odoo_version))


def make_ns_pkg_dirs(root, pkgs, force, with_ns_init_py):
    for pkg in pkgs.split("."):
        root = os.path.join(root, pkg)
        if not os.path.isdir(root):
            os.mkdir(root)
        init_path = os.path.join(root, "__init__.py")
        if with_ns_init_py:
            if not os.path.exists(init_path) or force:
                with open(init_path, "w") as f:
                    f.write(NS_INIT_PY)
        else:
            if os.path.exists(init_path):
                os.remove(init_path)
    return root


def make_default_setup_addon(addon_setup_dir, addon_dir, force, odoo_version_override):
    manifest = read_manifest(addon_dir)
    _, odoo_version, odoo_version_info = _get_version(
        addon_dir, manifest, odoo_version_override, git_post_version=False
    )
    addon_name = os.path.basename(os.path.realpath(addon_dir))
    setup_path = os.path.join(addon_setup_dir, "setup.py")
    odoo_addon = "True"
    if odoo_version_override:
        odoo_addon = "{'odoo_version_override': '%s'}" % odoo_version_override
    if not os.path.exists(setup_path) or force:
        with open(setup_path, "w") as f:
            f.write(SETUP_PY.format(odoo_addon=odoo_addon))
    odoo_addons_path = make_ns_pkg_dirs(
        addon_setup_dir,
        odoo_version_info["addons_ns"],
        force,
        with_ns_init_py=bool(odoo_version_info["namespace_packages"]),
    )
    link_path = os.path.join(odoo_addons_path, addon_name)
    # symlink to the main addon directory so we have a canonical structure:
    # odoo_addons/addon_name/...
    if os.path.exists(link_path) and force:
        os.remove(link_path)
    if not os.path.exists(link_path):
        os.symlink(os.path.relpath(addon_dir, odoo_addons_path), link_path)
    # setup.cfg
    if odoo_version_info["universal_wheel"]:
        setup_cfg_path = os.path.join(addon_setup_dir, "setup.cfg")
        with open(setup_cfg_path, "w") as f:
            f.write(SETUP_CFG_UNIVERSAL)


def make_default_setup_addons_dir(addons_dir, force, odoo_version_override):
    addons_setup_dir = os.path.join(addons_dir, "setup")
    if not os.path.exists(addons_setup_dir):
        os.mkdir(addons_setup_dir)
    readme_path = os.path.join(addons_setup_dir, "README")
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
        make_default_setup_addon(
            addon_setup_dir, addon_dir, force, odoo_version_override
        )


def make_default_meta_package(addons_dir, name, odoo_version_override):
    meta_install_requires = []
    odoo_versions = set()
    addons_setup_dir = os.path.join(addons_dir, "setup")
    metapackage_dir = os.path.join(addons_setup_dir, METAPACKAGE_SETUP_DIR)
    setup_py_file = os.path.join(metapackage_dir, "setup.py")
    setup_cfg_file = os.path.join(metapackage_dir, "setup.cfg")
    version_txt_file = os.path.join(metapackage_dir, "VERSION.txt")

    ignore_path = os.path.join(addons_setup_dir, IGNORE_FILENAME)
    ignore = _load_ignore_file(ignore_path)
    for addon_name in os.listdir(addons_dir):
        if addon_name in ignore:
            continue
        addon_dir = os.path.join(addons_dir, addon_name)
        if not is_installable_addon(addon_dir):
            continue
        meta_install_requires.append(
            make_pkg_requirement(addon_dir, odoo_version_override=odoo_version_override)
        )
        manifest = read_manifest(addon_dir)
        _, odoo_version, odoo_version_info = _get_version(
            addon_dir,
            manifest,
            odoo_version_override=odoo_version_override,
            git_post_version=False,
        )
        odoo_versions.add(odoo_version)

    if len(odoo_versions) == 0:
        sys.stderr.write("No installable addon found, not generating metapackage.\n")
        return
    if len(odoo_versions) > 1:
        raise RuntimeError(
            "not all addon are for the same " "Odoo version: %s" % (odoo_versions,)
        )

    odoo_version = list(odoo_versions)[0]

    install_requires_str = "[\n{}{}]".format(
        "".join(
            [
                " " * 8 + "'" + install_require + "',\n"
                for install_require in sorted(meta_install_requires)
            ]
        ),
        " " * 4,
    )

    setup_py = SETUP_PY_METAPACKAGE.format(
        name=name,
        odoo_version=odoo_version,
        pkg_name_pfx=odoo_version_info["pkg_name_pfx"],
        install_requires=install_requires_str,
    )

    if not os.path.exists(metapackage_dir):
        os.mkdir(metapackage_dir)

    if os.path.exists(setup_py_file):
        with open(setup_py_file, "r") as f:
            original_file_content = f.read()
    else:
        original_file_content = None

    if original_file_content is None or original_file_content != setup_py:
        if os.path.exists(version_txt_file):
            with open(version_txt_file, "r") as f:
                old_version = f.read().strip()
        else:
            old_version = None
        new_version = get_next_version(odoo_version, old_version)
        with open(version_txt_file, "w") as f:
            f.write(new_version)

    with open(setup_py_file, "w") as f:
        f.write(setup_py)

    if odoo_version_info["universal_wheel"]:
        with open(setup_cfg_file, "w") as f:
            f.write(SETUP_CFG_UNIVERSAL)


def get_next_version(odoo_version, old_version):
    version_date = datetime.date.today().strftime("%Y%m%d")
    if old_version:
        version_re = r"^[0-9]{1,2}\.0.(?P<date>[0-9]{8})\.(?P<index>[0-9]+)$"
        mo = re.match(version_re, old_version)
        if not mo:
            raise RuntimeError("Could not parse version {}".format(old_version))
        if mo.group("date") == version_date:
            index = int(mo.group("index")) + 1
        else:
            index = 0
    else:
        index = 0
    return "{odoo_version}.{version_date}.{index}".format(**locals())


def clean_setup_addons_dir(addons_dir, odoo_version_override):
    paths_to_remove = []
    empty = True

    addons_setup_dir = os.path.join(addons_dir, "setup")

    for addon_name in os.listdir(addons_setup_dir):
        addon_setup_dir = os.path.join(addons_setup_dir, addon_name)
        addon_setup_file = os.path.join(addon_setup_dir, "setup.py")
        odoo_lt_10_module_link = os.path.join(
            addon_setup_dir, "odoo_addons", addon_name
        )
        odoo_gt_10_module_link = os.path.join(
            addon_setup_dir, "odoo", "addons", addon_name
        )

        is_setup_dir = os.path.exists(addon_setup_file) and (
            os.path.islink(odoo_lt_10_module_link)
            or os.path.islink(odoo_gt_10_module_link)
        )
        if not is_setup_dir:
            # The entry will be skipped in case it's a file or
            # if the directory is not considered as a setup directory for an
            # addon
            continue

        addon_dir = os.path.join(addons_dir, addon_name)
        is_installable = is_installable_addon(addon_dir)
        try:
            # File or directory is not an addon. Skip it
            manifest = read_manifest(addon_dir)
        except NoManifestFound:
            manifest = None

        if not is_installable or not manifest:
            paths_to_remove.append(addon_setup_dir)
            continue

        empty = False

        _, odoo_version, odoo_version_info = _get_version(
            addon_dir,
            manifest,
            odoo_version_override=odoo_version_override,
            git_post_version=False,
        )
        odoo_series = _odoo_version_to_series(odoo_version)

        if odoo_series < 10:
            paths_to_remove.append(os.path.join(addon_setup_dir, "odoo"))
        if odoo_series >= 10:
            paths_to_remove.append(os.path.join(addon_setup_dir, "odoo_addons"))
        if odoo_series >= 11:
            paths_to_remove.append(os.path.join(addon_setup_dir, "odoo", "__init__.py"))
            paths_to_remove.append(
                os.path.join(addon_setup_dir, "odoo", "addons", "__init__.py")
            )
        if not odoo_version_info["universal_wheel"]:
            paths_to_remove.append(os.path.join(addon_setup_dir, "setup.cfg"))

    if empty:
        metapackage_dir = os.path.join(addons_setup_dir, METAPACKAGE_SETUP_DIR)
        paths_to_remove.append(metapackage_dir)

    # XXX we may want to clean metapackage_dir/setup.cfg if not universal_wheel
    for p in paths_to_remove:
        if os.path.isdir(p):
            shutil.rmtree(p)
        elif os.path.exists(p):
            os.unlink(p)


def check_setup_dir_is_git_clean(addons_dir):
    cmd = ["git", "diff", "--quiet", "--exit-code", "--", "setup"]
    if subprocess.call(cmd, cwd=addons_dir) != 0:
        return False
    cmd = ["git", "diff", "--quiet", "--exit-code", "--cached", "--", "setup"]
    if subprocess.call(cmd, cwd=addons_dir) != 0:
        return False
    cmd = [
        "git",
        "ls-files",
        "--other",
        "--exclude-standard",
        "--directory",
        "--",
        "setup",
    ]
    out = subprocess.check_output(cmd, cwd=addons_dir)
    if out:
        return False
    return True


def make_default_setup_commit_files(addons_dir):
    subprocess.check_call(["git", "add", "setup"], cwd=addons_dir)
    commit_needed = (
        subprocess.call(
            ["git", "diff", "--quiet", "--cached", "--exit-code", "--", "setup"],
            cwd=addons_dir,
        )
        != 0
    )
    if commit_needed:
        subprocess.check_call(
            ["git", "commit", "-m", "[ADD] setup.py", "--", "setup"], cwd=addons_dir
        )


def main(args=None):
    parser = argparse.ArgumentParser(
        description="Generate default setup.py for all addons in an "
        "Odoo addons directory"
    )
    parser.add_argument("--addons-dir", "-d", required=True)
    parser.add_argument("--force", "-f", action="store_true")
    parser.add_argument(
        "--odoo-version-override",
        help="Force Odoo version for situations where some "
        "addons versions do not start with the odoo "
        "version.",
    )
    parser.add_argument(
        "--metapackage",
        "-m",
        help="Create a metapackage using the given name. This "
        "package depends on all installable addons in ADDONS_DIR.",
    )
    parser.add_argument(
        "--clean",
        "-c",
        action="store_true",
        help="Clean the setup directory: remove setups of uninstallable "
        "addons, remove files corresponding to other Odoo versions, "
        "remove metapackage setup if there are no installable addons.",
    )
    parser.add_argument(
        "--commit", action="store_true", help="Git commit changes, if any."
    )
    args = parser.parse_args(args)

    if args.commit and not check_setup_dir_is_git_clean(args.addons_dir):
        sys.stderr.write(
            "You asked to git commit changes but the setup directory "
            "already has uncommitted changes, aborting.\n"
        )
        sys.exit(1)

    make_default_setup_addons_dir(
        args.addons_dir, args.force, args.odoo_version_override
    )

    if args.metapackage:
        make_default_meta_package(
            args.addons_dir, args.metapackage, args.odoo_version_override
        )

    if args.clean:
        # clean after so an empty meta package is removed
        clean_setup_addons_dir(args.addons_dir, args.odoo_version_override)

    if args.commit:
        make_default_setup_commit_files(args.addons_dir)


if __name__ == "__main__":
    main(sys.argv[1:])
