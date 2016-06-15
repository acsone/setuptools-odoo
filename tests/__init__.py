# -*- coding: utf-8 -*-
# Copyright © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class WorkingDirectoryKeeper(object):
    """A context manager to get back the working directory as it was before.
    If you want to stack working directory keepers, you need a new instance
    for each stage.
    """

    active = False

    def __enter__(self):
        if self.active:
            raise RuntimeError("Already in a working directory keeper !")
        self.wd = os.getcwd()
        self.active = True

    def __exit__(self, *exc_args):
        os.chdir(self.wd)
        self.active = False


working_directory_keeper = WorkingDirectoryKeeper()
