.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

===============
setuptools-odoo
===============

A lirary to help package Odoo addons with setuptools.

To use it, create a file name ``setup.py`` in the addon directory,
next to the ``__openerp__.py`` file:

  .. code:: python

    import setuptools
    import setuptools_odoo

    setup_keywords = setuptools_odoo.prepare(odoo_version='8.0')
    setuptools.setup(**setup_keywords)
