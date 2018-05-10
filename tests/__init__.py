# -*- coding: utf-8 -*-
# Copyright © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)
from contextlib import contextmanager
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


@contextmanager
def working_directory_keeper():
    wd = os.getcwd()
    try:
        yield
    finally:
        os.chdir(wd)
