# -*- coding: utf-8 -*-
# Copyright © 2020 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import os
import shutil
import textwrap
from functools import partial

from setuptools_odoo import get_requirements, make_default_setup

from . import DATA_DIR


def test_get_requirements(tmp_path):
    reqs_path = tmp_path / "reqs.txt"
    get_requirements.main(["--addons-dir", DATA_DIR, "-o", str(reqs_path)])
    assert reqs_path.read_text() == "astropy\npython-dateutil\n"


def test_get_requirements_include_addons(tmp_path):
    reqs_path = tmp_path / "reqs.txt"
    get_requirements.main(
        [
            "--addons-dir",
            os.path.join(DATA_DIR, "setup_custom_project", "odoo_addons"),
            "-o",
            str(reqs_path),
            "--include-addons",
        ]
    )
    assert reqs_path.read_text() == "odoo>=8.0a,<9.0a\npython-dateutil\n"


def test_get_requirements_header(tmp_path):
    reqs_path = tmp_path / "reqs.txt"
    get_requirements.main(
        ["--addons-dir", DATA_DIR, "-o", str(reqs_path), "--header", "# generated"]
    )
    assert reqs_path.read_text() == "# generated\nastropy\npython-dateutil\n"


def test_get_requirements_with_setup_dir(tmp_path):
    generated_dir = os.path.join(DATA_DIR, "setup")
    make_default_setup.main(["--addons-dir", DATA_DIR, "-f"])
    try:
        reqs_path = tmp_path / "reqs.txt"
        get_requirements.main(["--addons-dir", DATA_DIR, "-o", str(reqs_path)])
        assert reqs_path.read_text() == "astropy\npython-dateutil\n"
    finally:
        shutil.rmtree(generated_dir)


def test_get_requirements_override(tmp_path):
    reqs = get_requirements._get_requirements(
        DATA_DIR,
        get_metadata_overrides=partial(
            get_requirements._get_metadata_overrides_from_setup_dir,
            setup_dir="setup_reusable_addons",
        ),
    )
    assert reqs == ["astropy>=1.0", "python-dateutil"]


def test_get_requirements_empty(tmp_path):
    reqs_path = tmp_path / "reqs.txt"
    get_requirements.main(["--addons-dir", str(tmp_path), "-o", str(reqs_path)])
    assert not reqs_path.exists()


def test_get_requirements_empty_with_header(tmp_path):
    reqs_path = tmp_path / "reqs.txt"
    get_requirements.main(
        ["--addons-dir", str(tmp_path), "-o", str(reqs_path), "--header", "# header"]
    )
    assert not reqs_path.exists()


def test_get_requirements_empty_pre_exist(tmp_path):
    reqs_path = tmp_path / "reqs.txt"
    reqs_path.touch()
    get_requirements.main(["--addons-dir", str(tmp_path), "-o", str(reqs_path)])
    assert reqs_path.read_text() == ""


def test_get_requirements_empty_pre_exist_with_header(tmp_path):
    reqs_path = tmp_path / "reqs.txt"
    reqs_path.touch()
    get_requirements.main(
        ["--addons-dir", str(tmp_path), "-o", str(reqs_path), "--header", "# header"]
    )
    assert reqs_path.read_text() == "# header\n"


def test_get_requirements_include_addons_15(tmp_path):
    """Regression https://github.com/acsone/setuptools-odoo/issues/67"""
    addon1_dir = tmp_path / "addon1"
    addon1_dir.mkdir()
    (addon1_dir / "__manifest__.py").write_text(
        textwrap.dedent(
            u"""\
                {
                    "name": "addon1",
                    "version": "15.0.1.0.0",
                    "depends": ["addon2"],
                    "external_dependencies": {"python": ["httpx"]},
                }
            """
        )
    )
    addon2_dir = tmp_path / "addon2"
    addon2_dir.mkdir()
    (addon2_dir / "__manifest__.py").write_text(
        textwrap.dedent(
            u"""\
                {
                    "name": "addon2",
                    "version": "15.0.1.0.0",
                    "depends": ["another_addon"],
                }
            """
        )
    )
    reqs_path = tmp_path / "reqs.txt"
    get_requirements.main(["--addons-dir", str(tmp_path), "-o", str(reqs_path)])
    assert reqs_path.read_text() == "httpx\n"
    reqs_path.unlink()
    get_requirements.main(
        ["--addons-dir", str(tmp_path), "-o", str(reqs_path), "--include-addons"]
    )
    assert reqs_path.read_text() == textwrap.dedent(
        u"""\
            httpx
            odoo-addon-another_addon>=15.0dev,<15.1dev
            odoo>=15.0a,<15.1dev
        """
    )
