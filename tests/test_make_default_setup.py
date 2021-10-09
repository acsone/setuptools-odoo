# -*- coding: utf-8 -*-
# Copyright © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import datetime
import filecmp
import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest

import pytest

from setuptools_odoo import make_default_setup

from . import DATA_DIR


class TestMakeDefaultSetup(unittest.TestCase):
    def _assert_no_diff(self, dc):
        def _filter(names):
            return [
                name
                for name in names
                if not name.endswith(".pyc")
                and not name.endswith(".egg-info")
                and not name.endswith(".eggs")
            ]

        if dc.right.endswith("addon4"):
            # in addon4, we have a customized
            # setup.py to test depends and external_dependencies overrides
            return
        self.assertFalse(
            _filter(dc.left_only), "missing {} in {}".format(dc.left_only, dc.right)
        )
        self.assertFalse(
            _filter(dc.right_only),
            "unexpected {} in {}".format(dc.right_only, dc.right),
        )
        self.assertFalse(
            _filter(dc.diff_files), "differing {} in {}".format(dc.diff_files, dc.right)
        )
        for sub_dc in dc.subdirs.values():
            self._assert_no_diff(sub_dc)

    def test1(self):
        expected_dir = os.path.join(DATA_DIR, "setup_reusable_addons")
        generated_dir = os.path.join(DATA_DIR, "setup")
        make_default_setup.main(["--addons-dir", DATA_DIR, "-f"])
        dc = filecmp.dircmp(expected_dir, generated_dir)
        try:
            self._assert_no_diff(dc)
        finally:
            shutil.rmtree(generated_dir)

    def test_make_ns_pkg_dirs_1(self):
        opj = os.path.join
        tmpdir = tempfile.mkdtemp()
        try:
            d = make_default_setup.make_ns_pkg_dirs(tmpdir, "odoo_addons", False, True)
            self.assertEqual(d, opj(tmpdir, "odoo_addons"))
            self.assertTrue(os.path.isdir(d))
            self.assertTrue(os.path.isfile(opj(d, "__init__.py")))
        finally:
            shutil.rmtree(tmpdir)

    def test_make_ns_pkg_dirs_2(self):
        opj = os.path.join
        tmpdir = tempfile.mkdtemp()
        try:
            d = make_default_setup.make_ns_pkg_dirs(tmpdir, "odoo.addons", False, True)
            self.assertEqual(d, opj(tmpdir, "odoo", "addons"))
            self.assertTrue(os.path.isdir(d))
            self.assertTrue(os.path.exists(opj(tmpdir, "odoo", "__init__.py")))
            self.assertTrue(os.path.isfile(opj(d, "__init__.py")))
        finally:
            shutil.rmtree(tmpdir)

    def test_make_ns_pkg_dirs_3(self):
        opj = os.path.join
        tmpdir = tempfile.mkdtemp()
        try:
            d = make_default_setup.make_ns_pkg_dirs(tmpdir, "odoo.addons", False, False)
            self.assertEqual(d, opj(tmpdir, "odoo", "addons"))
            self.assertTrue(os.path.isdir(d))
            self.assertFalse(os.path.exists(opj(tmpdir, "odoo", "__init__.py")))
            self.assertFalse(os.path.exists(opj(d, "__init__.py")))
        finally:
            shutil.rmtree(tmpdir)


@pytest.mark.parametrize(
    ("series", "pkg_name_pfx", "pkg_version_specifier"),
    [
        ("8", "odoo8-addon", ""),
        ("15", "odoo-addon", ">=15.0dev,<15.1dev"),
    ],
)
def test_make_default_setup_metapackage(
    series, pkg_name_pfx, pkg_version_specifier, tmp_path
):
    addons_path = tmp_path / "tests"
    addons_path.mkdir()
    metapackage_dir = addons_path / "setup" / "_metapackage"
    setup_file = metapackage_dir / "setup.py"
    version_file = metapackage_dir / "VERSION.txt"
    today_date = datetime.date.today().strftime("%Y%m%d")
    expected_setup_file = textwrap.dedent(
        """\
            import setuptools

            with open('VERSION.txt', 'r') as f:
                version = f.read().strip()

            setuptools.setup(
                name="{pkg_name_pfx}s-tests",
                description="Meta package for tests Odoo addons",
                version=version,
                install_requires=[
                    '{pkg_name_pfx}-addon1{pkg_version_specifier}',
                ],
                classifiers=[
                    'Programming Language :: Python',
                    'Framework :: Odoo',
                    'Framework :: Odoo :: {series}.0',
                ]
            )
        """.format(
            series=series,
            pkg_name_pfx=pkg_name_pfx,
            pkg_version_specifier=pkg_version_specifier,
        )
    )

    addon1_path = addons_path / "addon1"
    addon1_path.mkdir()
    (addon1_path / "__manifest__.py").write_text(
        u"{{'version': '{series}.0.1.0.0'}}".format(series=series)
    )
    addon2_path = addons_path / "addon2"
    addon2_path.mkdir()
    (addon2_path / "__manifest__.py").write_text(
        u"{{'version': '{series}.0.1.0.0'}}".format(series=series)
    )
    make_default_setup.make_default_setup_addons_dir(str(addons_path), False, False)
    (addons_path / "setup" / ".setuptools-odoo-make-default-ignore").write_text(
        u"addon2\n"
    )
    make_default_setup.make_default_meta_package(
        str(addons_path), "tests", odoo_version_override=None
    )

    assert setup_file.read_text() == expected_setup_file

    assert version_file.read_text() == "{series}.0.{today_date}.0".format(
        series=series, today_date=today_date
    )

    # Create a new addon
    new_addon_path = addons_path / "addon99"
    new_addon_path.mkdir()
    (new_addon_path / "__manifest__.py").write_text(
        u"{{'version': '{series}.0.1.0.0'}}".format(series=series)
    )

    make_default_setup.make_default_setup_addons_dir(str(addons_path), False, False)
    make_default_setup.make_default_meta_package(
        str(addons_path), "tests", odoo_version_override=None
    )

    assert version_file.read_text() == "{series}.0.{today_date}.1".format(
        series=series, today_date=today_date
    ), "The version should have been incremented"


def test_make_default_setup_commit(tmpdir):
    with tmpdir.as_cwd():
        subprocess.check_call(["git", "init"])
        subprocess.check_call(["git", "config", "user.name", "test"])
        subprocess.check_call(["git", "config", "user.email", "test@example.com"])
        make_default_setup.main(["--addons-dir", ".", "--commit"])
        out = subprocess.check_output(["git", "ls-files"], universal_newlines=True)
        assert out == textwrap.dedent(
            """\
            setup/.setuptools-odoo-make-default-ignore
            setup/README
        """
        )


if __name__ == "__main__":
    unittest.main()
