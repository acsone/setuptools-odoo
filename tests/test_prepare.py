# -*- coding: utf-8 -*-
# Copyright © 2015-2018 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)
import os

from setuptools_odoo.core import (
    ODOO_VERSION_INFO,
    make_pkg_name,
    make_pkg_requirement,
    prepare_odoo_addon,
    prepare_odoo_addons,
)

from . import DATA_DIR, working_directory_keeper


def test_make_pkg_name():
    pkg_name = make_pkg_name(ODOO_VERSION_INFO["8.0"], "addon1")
    assert pkg_name == "odoo8-addon-addon1"


def test_make_pkg_requirement():
    addon_dir = os.path.join(DATA_DIR, "addon1")
    requirement = make_pkg_requirement(addon_dir)
    assert requirement == "odoo8-addon-addon1"


def test_addon1():
    addon_dir = os.path.join(DATA_DIR, "setup_reusable_addons", "addon1")
    with working_directory_keeper():
        os.chdir(addon_dir)
        keywords = prepare_odoo_addon()
        assert keywords == {
            "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
            "author_email": "support@odoo-community.org",
            "classifiers": [
                "Programming Language :: Python",
                "Framework :: Odoo",
                "License :: OSI Approved :: " "GNU Affero General Public License v3",
                "Development Status :: 4 - Beta",
            ],
            "description": "addon 1 summary",
            "include_package_data": True,
            "install_requires": ["odoo>=8.0a,<9.0a"],
            "python_requires": "~=2.7",
            "license": "AGPL-3",
            "long_description": "addon 1 readme content\n",
            "name": "odoo8-addon-addon1",
            "namespace_packages": ["odoo_addons"],
            "packages": ["odoo_addons"],
            "url": "https://acsone.eu/",
            "version": "8.0.1.0.0.99.dev4",
            "zip_safe": False,
        }


def test_addon2():
    addon_dir = os.path.join(DATA_DIR, "setup_reusable_addons", "addon2")
    with working_directory_keeper():
        os.chdir(addon_dir)
        keywords = prepare_odoo_addon()
        assert keywords == {
            "classifiers": ["Programming Language :: Python", "Framework :: Odoo"],
            "description": "addon 2 summary",
            "include_package_data": True,
            "install_requires": [
                "odoo8-addon-addon1",
                "odoo>=8.0a,<9.0a",
                "python-dateutil",
            ],
            "python_requires": "~=2.7",
            "name": "odoo8-addon-addon2",
            "namespace_packages": ["odoo_addons"],
            "packages": ["odoo_addons"],
            "version": "8.0.1.0.1",
            "zip_safe": False,
        }


def test_addon7():
    addon_dir = os.path.join(DATA_DIR, "setup_reusable_addons", "addon7")
    with working_directory_keeper():
        os.chdir(addon_dir)
        keywords = prepare_odoo_addon()
        assert keywords == {
            "classifiers": ["Programming Language :: Python", "Framework :: Odoo"],
            "description": "addon 7 summary",
            "include_package_data": True,
            "install_requires": ["odoo>=11.0a,<11.1dev"],
            "python_requires": ">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, " "!=3.3.*, !=3.4.*",
            "name": "odoo11-addon-addon7",
            "packages": ["odoo.addons"],
            "version": "11.0.1.0.1",
            "zip_safe": False,
        }


def test_addon8():
    addon_dir = os.path.join(DATA_DIR, "setup_reusable_addons", "addon8")
    with working_directory_keeper():
        os.chdir(addon_dir)
        keywords = prepare_odoo_addon()
        assert keywords == {
            "classifiers": ["Programming Language :: Python", "Framework :: Odoo"],
            "description": "addon 8 summary",
            "include_package_data": True,
            "install_requires": ["odoo>=12.0a,<12.1dev"],
            "python_requires": ">=3.5",
            "name": "odoo12-addon-addon8",
            "packages": ["odoo.addons"],
            "version": "12.0.1.0.1",
            "zip_safe": False,
        }


def test_addons_dir():
    addons_dir = os.path.join(DATA_DIR, "setup_custom_project")
    with working_directory_keeper():
        os.chdir(addons_dir)
        keywords = prepare_odoo_addons()
        assert keywords == {
            "include_package_data": True,
            "install_requires": ["odoo>=8.0a,<9.0a", "python-dateutil"],
            "python_requires": "~=2.7",
            "namespace_packages": ["odoo_addons"],
            "packages": ["odoo_addons"],
            "zip_safe": False,
        }
