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

    setup_keywords = setuptools_odoo.prepare()
    setuptools.setup(**setup_keywords)

Then, the addon can be deployed with usual setup.py commands such as::

    python setup.py install
    python setup.py develop

To run Odoo so it automatically discovers addons installed with this
method, start Odoo using odoo-server-autodiscover provided in this package.

It is of course highly recommanded to run all this inside a virtualenv.
