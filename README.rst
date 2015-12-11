.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3
.. image:: https://travis-ci.org/acsone/setuptools-odoo.svg?branch=master
   :target: https://travis-ci.org/acsone/setuptools-odoo
.. image:: https://coveralls.io/repos/acsone/setuptools-odoo/badge.svg?branch=master&service=github 
   :target: https://coveralls.io/github/acsone/setuptools-odoo?branch=master

===============
setuptools-odoo
===============

A library to help packaging Odoo addons with setuptools.

Packaging a single addon
------------------------

To be packaged with this library, the addon source code must have the 
following structure (assuming the addon is named ``<addon_name>``):

  .. code::

    setup.py
    odoo_addons/
    odoo_addons/__init__.py
    odoo_addons/<addon_name>/
    odoo_addons/<addon_name>/__openerp__.py
    odoo_addons/<addon_name>/...

where ``odoo_addons/__init__.py`` is a standard python namespace 
package declaration ``__init__.py``:

  .. code:: python

    __import__('pkg_resources').declare_namespace(__name__)

and where setup.py has the following content:

  .. code:: python

    import setuptools

    setuptools.setup(
        setup_requires=['setuptools-odoo'],
        odoo_addon=True,
    )

The usual setup() keyword arguments are computed automatically from the 
Odoo manifest file (``__openerp__.py``) and contain:

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

Packaging multiple addons
-------------------------

Addons that are intended to be reused or depended upon by other addons
MUST be packaged individually.  When preparing a project for a specific customer, 
it is common to prepare a collection of addons that are not intended to be 
depended upon by addons outside of the project. setuptools-odoo provides
tools to help you do that.

To be packaged with this library, your project must be structured according
to the following structure (assuming the addon is named ``<addon_name>``):

  .. code::

    setup.py
    odoo_addons/
    odoo_addons/__init__.py
    odoo_addons/<addon1_name>/
    odoo_addons/<addon1_name>/__openerp__.py
    odoo_addons/<addon1_name>/...
    odoo_addons/<addon2_name>/
    odoo_addons/<addon2_name>/__openerp__.py
    odoo_addons/<addon2_name>/...

where setup.py has the following content:

  .. code:: python

    import setuptools

    setuptools.setup(
        name='<your project package name>',
        version='<your version>',
        # ...any other setup() keyword
        setup_requires=['setuptools-odoo'],
        odoo_addons=True,
    )

The following setup() keyword arguments are computed automatically from the 
Odoo manifest files (``__openerp__.py``) and contain:

  * ``packages``: autodetected packages
  * ``namespace_packages``: ``['odoo_addons']``
  * ``zip_safe``: ``False``
  * ``include_package_data``: ``True``
  * ``install_requires``: dependencies on Odoo, any depending addon not found
    in the addons directory, and external python dependencies.

Specifying odoo_addons=True is the same as specifying odoo_addons='odoo_addons'.
If your odoo_addons namespace package directory is located elsewhere, say in 'src',
you can specify it using odoo_addons='src/odoo_addons'.

setuptools-odoo-make-default helper script
------------------------------------------

Since reusable addons are generally not structured using the namespace
package but instead collected in a directory with each subdirectory containing 
an addon, this package provides the ``setuptools-odoo-make-default`` script which
creates a ``setup.py`` for each addon according to the following structure:

  .. code::

    setup/
    setup/addon1/
    setup/addon1/setup.py
    setup/addon1/odoo_addons/
    setup/addon1/odoo_addons/__init__.py
    setup/addon1/odoo_addons/<addon1_name> -> ../../../<addon1_name>
    setup/addon2/odoo_addons/
    setup/addon2/odoo_addons/__init__.py
    setup/addon2/odoo_addons/<addon2_name> -> ../../../<addon2_name>
    <addon1_name>/
    <addon1_name>/__openerp__.py
    <addon1_name>/...
    <addon2_name>/
    <addon2_name>/__openerp__.py
    <addon2_name>/...

Helper API
----------

setuptools-odoo exposes the following public API.

  .. code::

    TODO...

Credits
-------

Author:

  * Stéphane Bidoul (ACSONE)
