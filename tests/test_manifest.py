# -*- coding: utf-8 -*-
# Copyright © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import os
import unittest

from setuptools_odoo.manifest import (
    read_manifest, is_installable_addon, NoManifestFound
)

from . import DATA_DIR


class TestManifest(unittest.TestCase):

    def test_read(self):
        addon_dir = os.path.join(DATA_DIR, 'addon1')
        manifest = read_manifest(addon_dir)
        assert 'version' in manifest

    def test_no_manifest(self):
        with self.assertRaises(NoManifestFound):
            read_manifest(DATA_DIR)

    def test_is_installable(self):
        addon1_dir = os.path.join(DATA_DIR, 'addon1')
        assert is_installable_addon(addon1_dir)
        addon3_dir = os.path.join(DATA_DIR, 'addon3_bad')
        assert not is_installable_addon(addon3_dir)
