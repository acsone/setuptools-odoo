setuptools-odoo
===============

.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3
.. image:: https://badge.fury.io/py/setuptools-odoo.svg
    :target: http://badge.fury.io/py/setuptools-odoo
.. image:: https://travis-ci.org/acsone/setuptools-odoo.svg?branch=master
   :target: https://travis-ci.org/acsone/setuptools-odoo
.. image:: https://coveralls.io/repos/acsone/setuptools-odoo/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/acsone/setuptools-odoo?branch=master

``setuptools-odoo`` is a library to help packaging Odoo addons with setuptools.
It mainly populates the usual ``setup.py`` keywords from the Odoo manifest files.

It enables the packaging and distribution of
Odoo addons using standard python infrastructure (ie
`setuptools <https://pypi.python.org/pypi/setuptools>`_,
`pip <https://pypi.python.org/pypi/pip>`_,
`wheel <https://pypi.python.org/pypi/wheel>`_,
and `pypi <https://pypi.python.org>`_).

.. Warning:: BACKWARD INCOMPATIBLE CHANGE

  From version 1.0.0b7 onwards, the package name structure is
  ``odoo<series>-addon-<addon_name>``. Before it was ``odoo-addon-<addon_name>``.
  This backward-incompatible change was necessary to enable easier
  publishing to pypi or other wheelhouses as discussed in `issue 6
  <https://github.com/acsone/setuptools-odoo/issues/6>`_.

  If you need to continue working with the previous
  naming scheme for some time, set the following environment
  variable ``SETUPTOOLS_ODOO_LEGACY_MODE=1``. This legacy scheme will
  be supported until version 1.1.

  It is highly recommanded to remove ``.eggs`` and ``*.egg-info``
  directories from editable source directories before using this new version.

.. contents::

.. Note:: The documentation below applies to Odoo 10+

  Odoo 8 and 9 are supported too, with the help of `odoo-autodiscover
  <https://pypi.python.org/pypi/odoo-autodiscover>`_. You must replace
  in the text below ``odoo.addons`` (the namespace) and ``odoo/addons``
  (the directory) by ``odoo_addons``.

Packaging a single addon
~~~~~~~~~~~~~~~~~~~~~~~~

To be packaged with this library, the addon source code must have the
following structure (assuming the addon is named ``<addon_name>``):

  .. code::

    setup.py
    odoo/
    odoo/__init__.py
    odoo/addons/
    odoo/addons/__init__.py
    odoo/addons/<addon_name>/
    odoo/addons/<addon_name>/__manifest__.py
    odoo/addons/<addon_name>/...

where ``odoo/__init__.py`` and ``odoo/addons/__init__.py`` are
standard python namespace package declaration ``__init__.py``:

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
Odoo manifest file (``__manifest__.py``) and contain:

  * ``name``: the package name, ``odoo<series>-addon-<addon_name>``
  * ``version``: the ``version`` key from the manifest
  * ``description``: the ``summary`` key from the manifest if it exists otherwise
    the ``name`` key from the manifest
  * ``long_description``: the content of the ``README.rst`` file if it exists,
    otherwise the ``description`` key from the manifest
  * ``url``: the ``website`` key from the manifest
  * ``license``: the ``license`` key from the manifest
  * ``packages``: autodetected packages
  * ``namespace_packages``: ``['odoo', 'odoo.addons']``
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
    pip install odoo<8|9|10>-addon-<addon name>

For Odoo 10, simply run Odoo normally with the ``odoo`` command. The
addons-path will be automatically populated with all places providing
odoo addons installed with this method.

For Odoo 8 or 9 start Odoo using the ``odoo-server-autodiscover`` or
``odoo-autodiscover.py`` scripts provided in the `odoo-autodiscover
<https://pypi.python.org/pypi/odoo-autodiscover>`_ package.

It is of course highly recommanded to run all this inside a virtualenv.

Packaging multiple addons
~~~~~~~~~~~~~~~~~~~~~~~~~

Addons that are intended to be reused or depended upon by other addons
MUST be packaged individually.  When preparing a project for a specific customer,
it is common to prepare a collection of addons that are not intended to be
depended upon by addons outside of the project. setuptools-odoo provides
tools to help you do that.

To be packaged with this library, your project must be structured according
to the following structure:

  .. code::

    setup.py
    odoo/
    odoo/__init__.py
    odoo/addons/
    odoo/addons/__init__.py
    odoo/addons/<addon1_name>/
    odoo/addons/<addon1_name>/__manifest__.py
    odoo/addons/<addon1_name>/...
    odoo/addons/<addon2_name>/
    odoo/addons/<addon2_name>/__manifest__.py
    odoo/addons/<addon2_name>/...

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
Odoo manifest files (``__manifest__.py``) and contain:

  * ``packages``: autodetected packages
  * ``namespace_packages``: ``['odoo', 'odoo.addons']``
  * ``zip_safe``: ``False``
  * ``include_package_data``: ``True``
  * ``install_requires``: dependencies on Odoo, any depending addon not found
    in the addons directory, and external python dependencies.

Controlling setuptools-odoo behaviour
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is possible to use a dictionary instead of ``True`` for the ``odoo_addon``
and ``odoo_addons`` keywords, in order to control their behaviour.

The following keys are supported:

  * ``depends_override``, used to precisely control odoo addons dependencies.
    Its value must be a dictionary mapping addon names to a package
    requirement string.
  * ``external_dependencies_override``, used to precisely control python
    external dependencies. Its value must be a dictionary with one ``python``
    key, with value a dictionary mapping python external dependencies to
    python package requirement strings.
  * ``odoo_version_override``, used to specify which Odoo series to use
    (8.0, 9.0, 10.0, etc) in case an addon version does not start with the Odoo
    series number. Use this only as a last resort, if you have no way to
    correct the addon version in its manifest.

For instance, if your module requires at least version 10.0.3.2.0 of
the connector addon, as well as at least version 0.5.5 of py-Asterisk,
your setup.py would look like this:

  .. code:: python

    import setuptools

    setuptools.setup(
        setup_requires=['setuptools-odoo'],
        odoo_addon={
            'depends_override': {
                'connector': 'odoo8-addon-connector>=10.0.3.2.0',
            },
            'external_dependencies_override': {
                'python': {
                    'Asterisk': 'py-Asterisk>=0.5.5',
                },
            },
        },
    )

setuptools-odoo-make-default helper script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since reusable addons are generally not structured using the namespace
package but instead collected in a directory with each subdirectory containing
an addon, this package provides the ``setuptools-odoo-make-default`` script which
creates a default ``setup.py`` for each addon according to the following structure:

  .. code::

    setup/
    setup/addon1/
    setup/addon1/setup.py
    setup/addon1/odoo/
    setup/addon1/odoo/__init__.py
    setup/addon1/odoo/addons/
    setup/addon1/odoo/addons/__init__.py
    setup/addon1/odoo/addons/<addon1_name> -> ../../../../<addon1_name>
    setup/addon2/setup.py
    setup/addon1/odoo/
    setup/addon1/odoo/__init__.py
    setup/addon2/odoo/addons/
    setup/addon2/odoo/addons/__init__.py
    setup/addon2/odoo/addons/<addon2_name> -> ../../../../<addon2_name>
    <addon1_name>/
    <addon1_name>/__manifest__.py
    <addon1_name>/...
    <addon2_name>/
    <addon2_name>/__manifest__.py
    <addon2_name>/...

Versioning
~~~~~~~~~~

setuptools-odoo does its best to detect if an addon has changed compared
to the version indicated in it's manifest. To this end it explores the
git log of the addon subtree.

If the last change to the addon corresponds to the version number in the manifest,
it is used as is for the python package version. Otherwise a counter
is incremented for each commit and the resulting version number has the following
form: [8|9].0.x.y.z.99.devN, N being the number of git commits since
the version change.

This scheme is compliant with the accepted python versioning scheme documented
in `PEP 440 <https://www.python.org/dev/peps/pep-0440/#developmental-releases>`_.

The 99 suffix is there to make sure it is considered as posterior to x.y.z.
(.postN is ignored by pip, as `specified in PEP 440
<https://www.python.org/dev/peps/pep-0440/#exclusive-ordered-comparison>`_,
and x.y.z.devN is considered anterior to x.y.z.).

.. Note::

  for pip to install a developmental version, it must be invoked with the --pre
  option.

Helper API
~~~~~~~~~~

setuptools-odoo exposes the following public API.

.. Note:: TODO

  Should you have a use case for using the setuptools-odoo internals,
  get in touch so we can review your needs and expose a clean API.

Useful links
~~~~~~~~~~~~

- pypi page: https://pypi.python.org/pypi/setuptools-odoo
- documentation: https://setuptools-odoo.readthedocs.io
- code repository: https://github.com/acsone/setuptools-odoo
- report issues at: https://github.com/acsone/setuptools-odoo/issues
- see also odoo-autodiscover: https://pypi.python.org/pypi/odoo-autodiscover 
  (for Odoo 8 and 9 only)

Credits
~~~~~~~

Author:

  - Stéphane Bidoul (`ACSONE <http://acsone.eu/>`_)

Many thanks to Daniel Reis who cleared the path, and Laurent Mignon who convinced
me it was possible to do it using standard Python setup tools and had the idea of
the odoo_addons namespace package.
