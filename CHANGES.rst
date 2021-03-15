Changes
~~~~~~~

.. Future (?)
.. ----------
.. -

2.7.1 (2021-03-15)
------------------
- ``setuptools-odoo-get-requirements --include-addons`` does not output
  local addons, as it is meant to list third party dependencies

2.7.0 (2021-03-13)
------------------
- [ADD] add new ``.N`` git post version strategy that adds a 6th digit with the
  number of commit since the latest manifest version change
- [ADD] implement the ``post_version_strategy_override`` keyword that was documented
  but not effective
- [ADD] allow overriding the post version strategy using the
  ``SETUPTOOLS_ODOO_POST_VERSION_STRATEGY_OVERRIDE`` environment variable
- [ADD] add ``--include-addons`` option to ``setuptools-odoo-get-requirements``,
  to output addon packages and odoo in addition to python external dependencies
- [UPD] update base addons lists

2.6.3 (2021-01-29)
------------------
- [UPD] update base addons lists

2.6.2 (2021-01-13)
------------------
- Fixed build system by opting-in to PEP 517

2.6.1 (unreleased)
------------------
- [UPD] update base addons lists

2.6.0 (2020-10-21)
------------------

- [ADD] Support for post version strategy override
- [ADD] setuptools-odoo-get-requirements to extract the list of external python
  dependencies from addon manifests

2.5.10 (2020-09-29)
-------------------
- [UPD] update base addons lists
- [ADD] Odoo 14 support

2.5.9 (2020-05-25)
------------------
- [FIX] further avoid depending on broken setuptools_scm 4.0.0

2.5.8 (2020-05-25)
------------------
- [FIX] avoid depending on broken setuptools_scm 4.0.0
- [UPD] update base addons lists

2.5.7 (2020-05-07)
------------------
- [UPD] update base addons lists

2.5.6 (2020-04-24)
------------------
- [UPD] update base addons lists

2.5.5 (2020-03-06)
------------------
- [UPD] update base addons lists

2.5.4 (2020-02-16)
------------------
- [UPD] update base addons lists

2.5.3 (2020-01-16)
------------------
- [IMP] update documentation for Odoo 12 and 13

2.5.2 (2020-01-16)
------------------
- [UPD] update base addons lists
- [ADD] pre-commit hook for setuptools-odoo-make-default

2.5.1 (2019-12-13)
------------------
- [FIX] Better detection of git repo root
- [UPD] update base addons lists

2.5.0 (2019-10-04)
------------------
- [ADD] new git autoversioning strategy (increase last digit instead of
  appending .99), will be used for Odoo 13
- [ADD] preliminary Odoo 13 support
- [ADD] new provisional public API that returns Python Package Metada 2.1 for
  and Odoo addon

2.4.1 (2018-11-05)
------------------
- [FIX] issue with make-default-setup metapackage generator
  now honors .setuptools-odoo-make-default-ignore

2.4.0 (2018-10-04)
------------------
- [IMP] update base addons lists, including Odoo 12

2.3.0 (2018-05-13)
------------------
- [FIX] remove tests from sdist (they work only within a proper
  git clone)
- [IMP] support development_status manifest key to generate
  corresponding pypi classifers
- [IMP] use pypa/setuptools_scm instead of the unmaintained
  setuptools-git as git file finder

2.2.1 (2018-05-08)
------------------
- [FIX] issue with make-default-setup --commit in empty directory

2.2.0 (2018-04-30)
------------------
- [IMP] silence some useless git warnings when looking for manifst
  in git history
- [IMP] when searching for manifest, look for __manifest__.py before
  __openerp__.py, this should slightly improve performance for what
  is becoming the most common case in recent Odoo versions
- [IMP] update base addons list for Odoo 8, 9, 10
- [IMP] load base addons list from resource files, making it easier
  to maintain these lists (using the udpated mk_base_addons script)
- [IMP] add OpenSSL and suds in external dependencies map

2.1.0 (2018-04-22)
------------------
- [FIX] give precedence to PKG-INFO over manifest to get version,
  so the git post version obtained when generating an sdist is
  preserved (before it would fall back in the manifest version
  when trying to build from an sdist outside of git)
- [IMP] update base addons list for Odoo 11.0

2.0.4 (2018-04-18)
------------------
- [FIX] setuptools-odoo-make-default: make metapackage a universal
  wheel for Odoo 11

2.0.3 (2018-04-18)
------------------
- [IMP] add --clean, --commit and --metapackage options to
  setuptools-odoo-make-default

2.0.2 (2017-10-07)
------------------
- [IMP] update base addons list for Odoo 11 (CE and EE)

2.0.1 (2017-10-02)
------------------
- [FIX] fix issue when odoo/addons has no __init__.py.

2.0.0 (2017-09-19)
------------------
- [IMP] update base addons list for Odoo 10.0
- [IMP] when setuptools extends a list-type keyword, prevent duplicate items
- [IMP] make tests pass with python 3
- [ADD] preliminary Odoo 11 support
- [IMP] BREAKING: remove LEGACY_MODE support
- [IMP] python_requires is now part of the generated keywords
- [CHG] In the classifiers, use Python instead of Python :: 2.7
  since we now have python_requires that is more precise

1.0.1 (2017-04-08)
------------------
- [ADD] add license classifier for the licenses commonly used in OCA

1.0.0 (2017-04-07)
------------------
- [ADD] support the brand new Framework :: Odoo classifier

1.0.0rc4 (2017-02-21)
---------------------
- [FIX] avoid setuptools-git version 1.2 as it is broken for
  our use case

1.0.0rc3 (2017-01-14)
---------------------
- [FIX] git based automatic postversioning was not working
  in situations where the manifest was renamed (eg when
  renaming ``__openerp__.py`` to ``__manifest__.py``)
- [IMP] support author email: since the Odoo manifest has
  no such concept this is currently just a special case
  when OCA is in the authors

1.0.0rc2 (2016-10-07)
---------------------
- [IMP] 10.0 addons now depend on the specific Odoo version again
  (>=10.0, <10.1dev)

1.0.0rc1 (2016-10-03)
---------------------
- [IMP] Odoo 10.0 support with addons in the odoo.addons namespace.
- [IMP] update base addons list for Odoo 9.0 and 10.0rc1

1.0.0b7 (2016-09-22)
--------------------
- [IMP] add __manifest__.py support for Odoo 10,
  drop __odoo__.py support which has never been supported by Odoo.
- [IMP] BREAKING: package names are now constructed along the
  following scheme: odoo{series}-addon-{addon_name} where series
  is 8, 9 or 10.

1.0.0b6 (2016-08-23)
--------------------
- [IMP] the odoo_addon and odoo_addons keyword now extend
  list keywords such as install_requires if they are present
  in setup.py (previously, it left them alone); this is useful
  to create a package that contains odoo addons in addition to
  other python packages
- [IMP] allow None as value for depends_override to disable
  the addition of an addon present in __openerp__.py 'depends'
  key to setup.py 'install_requires'
- [IMP] check if Odoo version is supported also in presence of
  odoo_version_override
- [ADD] preliminary OpenErp 7.0 support
- [ADD] --odoo-version-override to setuptools-odoo-make-default
  to use when there is no practical way to normalize addons versions
- [FIX] when using odoo_version_override, make sure the package
  version starts with the Odoo version, otherwise dependencies from
  other packages do not work
- [UPD] refresh base addons list for odoo 9c with new modules added
  over the last months

1.0.0b5 (2016-05-03)
--------------------
- [FIX] fix bug of previous release that prevented the packaging
  of a single auto_install addon

1.0.0b4 (2016-04-06)
--------------------
- [UPD] pycrypto in external dependencies map
- [ADD] setuptools-odoo-make-default now ignores addons listed
  in .setuptools-odoo-make-default-ignore; this is useful when
  some addons are manually included in another package (such as
  autoinstallable glue modules)
- [ADD] setuptools-odoo-make-default now generates README and
  .setuptools-odoo-make-default-ignore files at the root of
  the setup directory
- [IMP] the odoo_addon setup keyword now accepts several addons in the
  odoo_addons namespace, provided exactly one is installable and not
  auto installable. This is meant to package an addon together with one
  or more auto_installable glue modules.

1.0.0b3 (2016-02-10)
--------------------
- [ADD] mechanism to specify which Odoo version to use in dependencies
  (8.0, 9.0) in case some addons to be packaged have non-standard version
  numbers
- [ADD] support for addons without version number in their manifest
  (unfortunately there are some in the wild...)

1.0.0b2 (2016-01-26)
--------------------
- [ADD] mechanism to override dependencies, to allow addon authors to
  require minimal versions of dependent odoo addons, and to control external
  python dependencies

1.0.0b1 (2015-12-29)
--------------------
- [FIX] fix postversioning when running outside git directory
- [IMP] additional mappings for python external dependencies
- [ADD] make_pkg_name public api to convert an addon name to a python
  package name
- [ADD] make_pkg_requirement public api to obtain a valid package requirement
  for a given addon (same as make_pkg_name but includes requirement
  for the correct Odoo series)
- [FIX] crash in case a previous commit had a bad `__openerp__.py`

0.9.0 (2015-12-13)
------------------
- first beta
