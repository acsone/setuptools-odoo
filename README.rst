setuptools-odoo
===============

.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3
.. image:: https://badge.fury.io/py/setuptools-odoo.svg
    :target: http://badge.fury.io/py/setuptools-odoo
.. image:: https://results.pre-commit.ci/badge/github/acsone/setuptools-odoo/master.svg
   :target: https://results.pre-commit.ci/latest/github/acsone/setuptools-odoo/master
   :alt: pre-commit.ci status
.. image:: https://coveralls.io/repos/acsone/setuptools-odoo/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/acsone/setuptools-odoo?branch=master

⚠️ This project is progressively being deprecated. Please consider using `whool
<https://github.com/sbidoul/whool>`_ for packaging individual Odoo addons, and
`hatch-odoo <https://github.com/acsone/hatch-odoo>`_ to build complete projects that
include Odoo addons. ⚠️

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

  * Odoo version 8, 9, 10, 11, 12, 13, 14, 15 and 16 are supported (see notes in the
    documentation for implementation differences).
  * To install addons packaged with this tool, any pip version that
    supports the wheel package format should work (ie pip >= 1.4).
  * For any advanced use such as installing from source, installing from
    git, packaging wheels etc, you need a recent version of pip (>= 9.0.1).
  * Finally, if you are using Odoo 8, 9 or 10, you need to install
    `odoo-autodiscover <https://pypi.python.org/pypi/odoo-autodiscover>`_
    (``pip install odoo-autodiscover``) to provide automatic extension
    of the addons path (and workaround a bug with setuptools > 31 and Odoo 10).
    odoo-autodiscover is *not* necessary for Odoo >= 11.

Packaging a single addon
~~~~~~~~~~~~~~~~~~~~~~~~

To be packaged with this library, the addon source code must have the
following structure (assuming the addon is named ``<addon_name>``):

  .. code::

    # Odoo >= 11
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
declaration ``__init__.py`` (note ``__init__.py`` is absent for Odoo >= 11):

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

Then, the addon can be deployed and packaged with usual ``pip`` commands such as:

  .. code:: shell

    pip install odoo<8|9|10|11|12|13|14>-addon-<addon name>
    pip install "git+https://github.com/OCA/<repo>#subdirectory=setup/<addon name>"
    pip install "git+https://github.com/OCA/<repo>@<branch or reference>#subdirectory=setup/<addon name>"
    pip install -e .
    pip wheel .
    python -m build

.. note::

   Please make sure to use the latest pip version.

.. note::

   When using Python 2 (Odoo 8, 9, 10), please install ``odoo-autodiscover>=2`` so the
   addons-path is automatically populated with all places providing odoo addons
   installed with this method.

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

    # Odoo >= 11
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
    ``['odoo_addons']`` (Odoo 8, 9), absent for Python 3 (Odoo 11 and later)
  * ``zip_safe``: ``False``
  * ``include_package_data``: ``True``
  * ``install_requires``: dependencies on Odoo, any depending addon not found
    in the addons directory, and external python dependencies.
  * ``python_requires``

Installing Odoo CE and EE addons
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``setuptools-odoo`` has built-in knowledge of the addons that are part of the Odoo
Community and Enterprise editions. Dependencies on these addons are condidered to be
satisfied by the ``odoo`` distribution.

This means Odoo must be *installed* in your python environment.

As of Odoo 8 to 16, a good way to install Odoo is in a virtual environment. There are
several possibilities, but the following bash commands should get you started:

.. code:: console

  $ python3 -m venv ./venv
  $ source ./venv/bin/activate
  (venv) $ python3 -m pip install --upgrade pip wheel
  (venv) $ python3 -m pip install -r ./odoo/requirements.txt
  (venv) $ python3 -m pip install -e ./odoo

After that, ``./venv/bin/pip list`` will show ``odoo`` as part of the installed
projects, and running ``./venv/bin/odoo`` will start Odoo with a proper addons path.

If you need to add the Odoo Enterprise addons, you can make them visible to Odoo using
the ``--addons-path`` Odoo option, or package them in a multi-addons project that you
pip install, as explained above.

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
    a python package requirement specifier or list of specifiers.
  * ``odoo_version_override``, used to specify which Odoo series to use
    (8.0, 9.0, 10.0, 11.0, ...) in case an addon version does not start with the Odoo
    series number. Use this only as a last resort, if you have no way to
    correct the addon version in its manifest.
  * ``post_version_strategy_override``, used to specify how the git commits are used
    to amend the version found in the manifest (see the Versioning_ section below).

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
                    'somepkg': [
                      'somepkg<3 ; python_version < "3"',
                      'somepkg>=3 ; python_version > "3"',
                    ]
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

    # Odoo >= 11
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

Available options::

  usage: setuptools-odoo-make-default [-h] --addons-dir ADDONS_DIR [--force]
                                      [--odoo-version-override ODOO_VERSION_OVERRIDE]
                                      [--metapackage METAPACKAGE] [--clean]
                                      [--commit]

  Generate default setup.py for all addons in an Odoo addons directory

  optional arguments:
    -h, --help            show this help message and exit
    --addons-dir ADDONS_DIR, -d ADDONS_DIR
    --force, -f
    --odoo-version-override ODOO_VERSION_OVERRIDE
                          Force Odoo version for situations where some addons
                          versions do not start with the odoo version.
    --metapackage METAPACKAGE, -m METAPACKAGE
                          Create a metapackage using the given name. This
                          package depends on all installable addons in
                          ADDONS_DIR.
    --clean, -c           Clean the setup directory: remove setups of
                          uninstallable addons, remove files corresponding to
                          other Odoo versions, remove metapackage setup if there
                          are no installable addons.
    --commit              Git commit changes, if any.

``setuptools-odoo-make-default`` is also available as a `pre-commit
<https://pre-commit.com/>`_ hook. To use it, you can add such an entry
in your `.pre-commit-config.yaml`:

.. code:: yaml

  repos:
    - repo: https://github.com/acsone/setuptools-odoo
      rev: 2.5.2
      hooks:
        - id: setuptools-odoo-make-default

setuptools-odoo-get-requirements helper script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since it is a common practice in the Odoo world to have a file named
``requirements.txt`` at the repository root, this script helps generating it
from the external dependencies declared in addons manifests.::

  usage: setuptools-odoo-get-requirements [-h] [--addons-dir ADDONS_DIR] [--output OUTPUT]

  Print external python dependencies for all addons in an Odoo addons directory.
  If dependencies overrides are declared in setup/{addon}/setup.py, they are
  honored in the output.

  optional arguments:
    -h, --help            show this help message and exit
    --addons-dir ADDONS_DIR, -d ADDONS_DIR
                          addons directory (default: .)
    --output OUTPUT, -o OUTPUT
                          output file (default: stdout)
    --header HEADER       output file header
    --include-addons      Include addons and odoo requirements in addition to
                          python external dependencies (default: false).


Versioning
~~~~~~~~~~

By default, setuptools-odoo does its best to detect if an addon has changed
compared to the version indicated in it's manifest. To this end it explores the
git log of the addon subtree.

If the last change to the addon corresponds to the version number in the manifest,
it is used as is for the python package version. Otherwise a counter
is incremented for each commit and the resulting version number includes that counter.

The default strategy depends on the Odoo series. It has the following form,
N being the number of git commits since the version change.

- Strategy ``.99.devN`` is the default for series 8 to 12 and yields
  ``[8|9|10|11|12].0.x.y.z.99.devN``.
- Strategy ``+1.devN`` is the default for series 13 and 14 and yields
  ``[13|14].0.x.y.z+1.devN``.
- Strategy ``.N`` is the default for series 15 and later, and
  adds a digit, typically yielding ``[series].0.x.y.z.N``.
- Strategy ``none`` is not used by default and disables the post
  versioning mechanism, yielding the version found in the manifest.

These schemes are compliant with the accepted python versioning scheme documented
in `PEP 440 <https://www.python.org/dev/peps/pep-0440/#developmental-releases>`_.

The default strategy can be overridden using the
``post_version_strategy_override`` keyword or the
``SETUPTOOLS_ODOO_POST_VERSION_STRATEGY_OVERRIDE`` environment variable. If set
and not empty, the environment variable has priority over the ``setup.py``
keyword.

.. Note::

  For ``pip`` to install a developmental version, it must be invoked with the ``--pre``
  option.

Public API
~~~~~~~~~~

The ``setuptools_odoo`` package exposes a provisional public API.

* ``get_addon_metadata(addon_dir, ...)`` returns an ``email.message.Message``
  compliant with `Python Core metadata specifications
  <https://packaging.python.org/en/latest/specifications/core-metadata/>`_.

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

Contributors

  - Benjamin Willig
  - Matteo Bilotta

Many thanks to Daniel Reis who cleared the path, and Laurent Mignon who convinced
me it was possible to do it using standard Python packaging tools and had the idea of
the odoo_addons namespace package.
