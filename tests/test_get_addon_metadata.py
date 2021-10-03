# -*- coding: utf-8 -*-
# Copyright © 2019 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import os
import textwrap

from setuptools_odoo import get_addon_metadata

from . import DATA_DIR

try:
    from itertools import zip_longest
except ImportError:  # py27
    from itertools import izip_longest as zip_longest


def _assert_msg(msg, expected_items, expected_payload=None):
    for msg_item, expected_item in zip_longest(msg.items(), expected_items):
        assert msg_item == expected_item
    if expected_payload:
        assert msg.get_payload() == expected_payload


def test_addon1():
    addon_dir = os.path.join(DATA_DIR, "addon1")
    metadata = get_addon_metadata(addon_dir)
    _assert_msg(
        metadata,
        [
            ("Metadata-Version", "2.2"),
            ("Name", "odoo8-addon-addon1"),
            ("Version", "8.0.1.0.0.99.dev4"),
            ("Requires-Python", "~=2.7"),
            ("Requires-Dist", "odoo>=8.0a,<9.0a"),
            ("Summary", "addon 1 summary"),
            ("Home-page", "https://acsone.eu/"),
            ("License", "AGPL-3"),
            ("Author", "ACSONE SA/NV, Odoo Community Association (OCA)"),
            ("Author-email", "support@odoo-community.org"),
            ("Classifier", "Programming Language :: Python"),
            ("Classifier", "Framework :: Odoo"),
            (
                "Classifier",
                "License :: OSI Approved :: " "GNU Affero General Public License v3",
            ),
            ("Classifier", "Development Status :: 4 - Beta"),
        ],
    )


def test_pkg_info(tmp_path):
    """Test that PKG-INFO is used to obtain name and version"""
    addon_dir = tmp_path / "odoo12-addon-test_addon-12.0.1.0.0.dev5"
    addon_dir.mkdir()
    (addon_dir / "__manifest__.py").write_text(
        textwrap.dedent(
            u"""\
                {
                    "name": "test addon",
                    "version": "12.0.1.0.0",
                }
            """
        )
    )
    (addon_dir / "PKG-INFO").write_text(
        textwrap.dedent(
            u"""\
                Name: odoo12-addon-test_addon
                Version: 12.0.1.0.0.dev5
            """
        )
    )
    metadata = get_addon_metadata(
        str(addon_dir), precomputed_metadata_path=str(addon_dir / "PKG-INFO")
    )
    assert metadata["Name"] == "odoo12-addon-test_addon"
    assert metadata["Version"] == "12.0.1.0.0.dev5"
    assert metadata["Requires-Dist"] == "odoo>=12.0a,<12.1dev"
