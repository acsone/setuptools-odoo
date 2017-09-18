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

.. contents::

Requirements
~~~~~~~~~~~~

The following prerequisites apply:

  * Odoo version 8, 9, 10 and 11 are supported (see notes in the documentation
    for implementation differences).
  * To install addons packaged with this tool, any pip version that
    supports the wheel package format should work (ie pip >= 1.4).
  * For any advanced use such as installing from source, installing from
    git, packaging wheels etc, you need a recent version of pip (>= 9.0.1).
  * Finally, you need to install `odoo-autodiscover
    <https://pypi.python.org/pypi/odoo-autodiscover>`_ 
    (``pip install odoo-autodiscover``) to provide automatic extension
    of the addons path (and workaround a bug with setuptools > 31 and Odoo 10).

Packaging a single addon
~~~~~~~~~~~~~~~~~~~~~~~~

To be packaged with this library, the addon source code must have the
following structure (assuming the addon is named ``<addon_name>``):

  .. code::

    # Odoo 11
    setup.py
    odoo/
    odoo/addons/
    odoo/addons/<addon_name>/
    odoo/addons/<addon_name>/__manifest__.py
    odoo/addons/<addon_name>/...

    # Odoo 10
    setup.py
    odoo/
    odoo/__init__.py
    odoo/addons/
    odoo/addons/__init__.py
    odoo/addons/<addon_name>/
    odoo/addons/<addon_name>/__manifest__.py
    odoo/addons/<addon_name>/...

    # Odoo 8, 9
    setup.py
    odoo_addons/
    odoo_addons/__init__.py
    odoo_addons/<addon_name>/
    odoo_addons/<addon_name>/__openerp__.py
    odoo_addons/<addon_name>/...

where ``odoo/__init__.py``, ``odoo/addons/__init__.py``,
and ``odoo_addons/__init__.py`` are standard python namespace package
declaration ``__init__.py`` (note absent ``__init__.py`` for Odoo 11):

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
Odoo manifest file (``__manifest__.py`` or ``__openerp__.py``) and contain:

  * ``name``: the package name, ``odoo<series>-addon-<addon_name>``
  * ``version``: the ``version`` key from the manifest
  * ``description``: the ``summary`` key from the manifest if it exists otherwise
    the ``name`` key from the manifest
  * ``long_description``: the content of the ``README.rst`` file if it exists,
    otherwise the ``description`` key from the manifest
  * ``url``: the ``website`` key from the manifest
  * ``license``: the ``license`` key from the manifest
  * ``packages``: autodetected packages
  * ``namespace_packages``: ``['odoo', 'odoo.addons']`` (Odoo 10) or
    ``['odoo_addons']`` (Odoo 8, 9), absent for Odoo 11
  * ``zip_safe``: ``False``
  * ``include_package_data``: ``True``
  * ``install_requires``: dependencies to Odoo, other addons (except official
    odoo community and enterprise addons, which are brought by the Odoo dependency)
    and python libraries.
  * ``python_requires``

Then, the addon can be deployed and packaged with usual ``setup.py``
or ``pip`` commands such as:

  .. code:: shell

    python setup.py install
    python setup.py develop
    python setup.py bdist_wheel
    pip install odoo<8|9|10|11>-addon-<addon name>
    pip install -e .
    pip install -e git+https://github.com/OCA/<repo>/<addon>#egg=odoo<8|9|10|11>-addon-<addon name>\&subdirectory=setup/<addon name>

.. note::

   When using pip to install from source, the `-e` option is important
   because of `pip issue #3500 <https://github.com/pypa/pip/issues/3500>`_.
   The `-e` option has the huge advantage of letting `pip freeze` produce
   meaningful output.

When ``odoo-server-autodiscover`` is installed, The
addons-path is automatically populated with all places providing
odoo addons installed with this method.

It is of course highly recommanded to run in a virtualenv.

  .. note:: Odoo 8, 9 namespace.

     Although the addons are packaged in the ``odoo_addons`` namespace,
     the code can still import them using ``import odoo.addons....``.
     ``odoo_addons`` must never appear in the code, it is just a packaging
     peculiarity for Odoo 8 and 9 only, and does not require any change
     to the addons source code.

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

    # Odoo 11
    setup.py
    odoo/
    odoo/addons/
    odoo/addons/<addon1_name>/
    odoo/addons/<addon1_name>/__manifest__.py
    odoo/addons/<addon1_name>/...
    odoo/addons/<addon2_name>/
    odoo/addons/<addon2_name>/__manifest__.py
    odoo/addons/<addon2_name>/...

    # Odoo 10
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

    # Odoo 8, 9
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
Odoo manifest files (``__manifest__.py`` or ``__openerp__.py``) and contain:

  * ``packages``: autodetected packages
  * ``namespace_packages``: ``['odoo', 'odoo.addons']`` (Odoo 10) or
    ``['odoo_addons']`` (Odoo 8, 9), absent for Odoo 11
  * ``zip_safe``: ``False``
  * ``include_package_data``: ``True``
  * ``install_requires``: dependencies on Odoo, any depending addon not found
    in the addons directory, and external python dependencies.
  * ``python_requires``

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
    (8.0, 9.0, 10.0, 11.0) in case an addon version does not start with the Odoo
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
                'connector': 'odoo10-addon-connector>=10.0.3.2.0',
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

    # Odoo 11
    setup/
    setup/addon1/
    setup/addon1/setup.py
    setup/addon1/odoo/
    setup/addon1/odoo/addons/
    setup/addon1/odoo/addons/<addon1_name> -> ../../../../<addon1_name>
    setup/addon2/setup.py
    setup/addon1/odoo/
    setup/addon2/odoo/addons/
    setup/addon2/odoo/addons/<addon2_name> -> ../../../../<addon2_name>
    <addon1_name>/
    <addon1_name>/__manifest__.py
    <addon1_name>/...
    <addon2_name>/
    <addon2_name>/__manifest__.py
    <addon2_name>/...

    # Odoo 10
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

    # Odoo 8, 9
    setup/
    setup/addon1/
    setup/addon1/setup.py
    setup/addon1/odoo_addons/
    setup/addon1/odoo_addons/__init__.py
    setup/addon1/odoo_addons/<addon1_name> -> ../../../<addon1_name>
    setup/addon2/setup.py
    setup/addon2/odoo_addons/
    setup/addon2/odoo_addons/__init__.py
    setup/addon2/odoo_addons/<addon2_name> -> ../../../<addon2_name>
    <addon1_name>/
    <addon1_name>/__openerp__.py
    <addon1_name>/...
    <addon2_name>/
    <addon2_name>/__openerp__.py
    <addon2_name>/...

Versioning
~~~~~~~~~~

setuptools-odoo does its best to detect if an addon has changed compared
to the version indicated in it's manifest. To this end it explores the
git log of the addon subtree.

If the last change to the addon corresponds to the version number in the manifest,
it is used as is for the python package version. Otherwise a counter
is incremented for each commit and the resulting version number has the following
form: [8|9|10|11].0.x.y.z.99.devN, N being the number of git commits since
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

Credits
~~~~~~~

Author:

  - Stéphane Bidoul (`ACSONE <http://acsone.eu/>`_)

Many thanks to Daniel Reis who cleared the path, and Laurent Mignon who convinced
me it was possible to do it using standard Python setup tools and had the idea of
the odoo_addons namespace package.
