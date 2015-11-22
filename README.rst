.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

===============
setuptools-odoo
===============

A library to help packaging Odoo addons with setuptools.

To be packaged with this library, the addon source code must have the 
following structure (assuming the addon is named ``<addon_name>``)::

    setup.py
    odoo_addons/
    odoo_addons/__init__.py
    odoo_addons/<addon_name>/
    odoo_addons/<addon_name>/__openerp__.py
    odoo_addons/<addon_name>/...

where ``odoo_addons/__init__.py`` is a standard python namespace 
package ``__init__.py``:

  .. code:: python

    __import__('pkg_resources').declare_namespace(__name__)

and where setup.py has the following content:

  .. code:: python

    import setuptools
    import setuptools_odoo

    setup_keywords = setuptools_odoo.prepare('<addon_name>')
    setuptools.setup(**setup_keywords)

in which ``setup_keywords`` is generated from the addon manifest file 
(``__openerp__.py``) and contains:

  * ``name``: the package name, ``odoo-addon-<addon_name>``
  * ``version``: the ``version`` key from the manifest
  * ``description``: the ``summary`` key from the manifest if it exists otherwise
    the ``name`` key from the manifest
  * ``long_description``: the content of the ``README.rst`` file if it exists,
    otherwise the ``description`` key from the manifest
  * ``url``: the ``website`` key from the manifest
  * ``licence``: the ``license`` key from the manifest
  * ``packages``: autodetected packages
  * ``namespace_packages``: ``['odoo_addons']``
  * ``zip_safe``: ``False``
  * ``include_package_data``: ``True``
  * ``install_requires``: dependencies to Odoo, other addons (except official
    odoo addons, which are brought by the Odoo dependency) and python libraries.

Then, the addon can be deployed and packaged with usual ``setup.py``
or ``pip`` commands such as:

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

setuptools-odoo-make-default helper script
------------------------------------------

Since reusable addons are generally not structured using the namespace
package but instead collected in a directory with each subdirectory containing 
an addon, this package provides the ``setuptools-odoo-make-default`` script which
creates a ``setup.py`` for each addon according to the following structure::

    setup/
    setup/addon1/
    setup/addon1/setup.py
    setup/addon1/odoo_addons/
    setup/addon1/odoo_addons/__init__.py
    setup/addon1/odoo_addons/addon1 -> ../../../addon1
    setup/addon2/odoo_addons/
    setup/addon2/odoo_addons/__init__.py
    setup/addon2/odoo_addons/addon1 -> ../../../addon2
    addon1/
    addon1/__openerp__.py
    addon1/...
    addon2/
    addon2/__openerp__.py
    addon2/...

Helper API
----------

When creating a customer project containing several addons that are intended 
to be deployed together and not being depended upon by other addons, this package
provide an API to enumerate all dependencies of a set of addons, allowing the 
creation of the following project structure::

    TODO

Credits
-------

Author:

  * Stéphane Bidoul (ACSONE)
