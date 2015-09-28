# -*- coding: utf-8 -*-
# © 2015 ACSONE SA/NV
# License LGPLv3+ or later (http://www.gnu.org/licenses/lgpl.html).

import setuptools

setuptools.setup(
    name='setuptools-odoo',
    version='0.1.0',
    description='A library to help package Odoo addons with setuptools',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Odoo',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: '
            'GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
    ],
    licence='LGPLv3+',
    author='ACSONE SA/NV',
    author_email='info@acsone.eu',
    url='http://github.com/acsone/setuptools-odoo',
    packages=['setuptools_odoo'],
)
