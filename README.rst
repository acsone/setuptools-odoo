.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

===============
setuptools-odoo
===============

A library to help packaging Odoo addons with setuptools.

To use it, create a file name ``setup.py`` in the addon directory,
next to the ``__openerp__.py`` file:

  .. code:: python

    import setuptools
    import setuptools_odoo

    setup_keywords = setuptools_odoo.prepare(addon_name=<addon_name>)
    setuptools.setup(**setup_keywords)

Then, the addon can be deployed and packaged with usual ``setup.py``
or `pip`` commands such as:

  .. code:: shell

    python setup.py install
    python setup.py develop
    python setup.py bdist_wheel
    pip install .
    pip install -e .
    pip install odoo-addon-<addon name>

To run Odoo so it automatically discovers addons installed with this
method, start Odoo using the ``odoo-server-autodiscover`` or
``odoo-autodiscover.py`` scripts provided in the `odoo-autodiscover
<https://github.com/acsone/odoo-autodiscover>`_ package.

It is of course highly recommanded to run all this inside a virtualenv.

Credits
-------

Author:

  * Stéphane Bidoul (ACSONE)
