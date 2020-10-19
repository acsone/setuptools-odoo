# -*- coding: utf-8 -*-
# Copyright © 2020 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import os
import shutil
from functools import partial

from setuptools_odoo import get_requirements, make_default_setup

from . import DATA_DIR


def test_get_requirements(tmp_path):
    reqs_path = tmp_path / "reqs.txt"
    get_requirements.main(["--addons-dir", DATA_DIR, "-o", str(reqs_path)])
    assert reqs_path.read_text() == "astropy\npython-dateutil\n"


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
    assert reqs_path.read_text() == "\n"
