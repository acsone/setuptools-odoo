# -*- coding: utf-8 -*-
# © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import filecmp
import os
import shutil
import unittest

from setuptools_odoo import make_default_setup

from . import DATA_DIR


class TestMakeDefaultSetup(unittest.TestCase):

    def _assert_no_diff(self, dc):
        def _filter(l):
            return [i for i in l
                    if not i.endswith('.pyc') and
                    not i.endswith('.egg-info')]
        if dc.right.endswith('addon4'):
            # in addon4, we have a customized
            # setup.py to test depends and external_dependencies overrides
            return
        self.assertFalse(_filter(dc.left_only),
                         "missing %s in %s" % (dc.left_only, dc.right))
        self.assertFalse(_filter(dc.right_only),
                         "unexpected %s in %s" % (dc.right_only, dc.right))
        self.assertFalse(_filter(dc.diff_files),
                         "differing %s in %s" % (dc.diff_files, dc.right))
        for sub_dc in dc.subdirs.values():
            self._assert_no_diff(sub_dc)

    def test1(self):
        expected_dir = os.path.join(DATA_DIR, 'setup_reusable_addons')
        generated_dir = os.path.join(DATA_DIR, 'setup')
        make_default_setup.main(['--addons-dir', DATA_DIR, '-f'])
        dc = filecmp.dircmp(expected_dir, generated_dir)
        try:
            self._assert_no_diff(dc)
        finally:
            shutil.rmtree(generated_dir)


if __name__ == '__main__':
    unittest.main()
