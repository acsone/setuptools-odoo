#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2015-2016 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import setuptools

setuptools.setup(
    name='setuptools-odoo',
    use_scm_version=True,
    description='A library to help package Odoo addons with setuptools',
    long_description='\n'.join((
        open('README.rst').read(),
        open('CHANGES.rst').read(),
    )),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: '
        'GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: POSIX',  # because we use symlinks
        'Programming Language :: Python :: 2.7',
    ],
    license='LGPLv3',
    author='ACSONE SA/NV',
    author_email='info@acsone.eu',
    url='http://github.com/acsone/setuptools-odoo',
    packages=[
        'setuptools_odoo',
    ],
    install_requires=[
        'setuptools',
        'setuptools-git',
    ],
    setup_requires=[
        'setuptools_scm'
    ],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            "setuptools-odoo-make-default="
            "setuptools_odoo.make_default_setup:main",
        ],
        "distutils.setup_keywords": [
            "odoo_addon = setuptools_odoo.setup_keywords:odoo_addon",
            "odoo_addons = setuptools_odoo.setup_keywords:odoo_addons",
        ],
    },
)
