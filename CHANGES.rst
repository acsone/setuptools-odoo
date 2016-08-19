Changes
~~~~~~~

.. Future (?)
.. ----------
.. -

1.0.0b6 (????-??-??)
--------------------
- [UPD] Refresh base addons list for odoo 9c
- [IMP] the odoo_addon and odoo_addons keyword now extend
  list keywords such as install_requires if they are present
  in setup.py (previously, it left them alone); this is useful
  to create a package that contains odoo addons in addition to
  other python packages
- [IMP] allow None as value for depends_override to disable
  the addition of an addon present in __openerp__.py 'depends'
  key to setup.py 'install_requires'.
- [IMP] check Odoo version support in presence of
  odoo_version_override too.
- [ADD] preliminary OpenErp 7.0 support
- [ADD] --odoo-version-override to setuptools-odoo-make-default
  to use when there is no practical way to normalize addons versions
- [FIX] when using odoo_version_override, make sure the package
  version starts with the Odoo version, otherwise dependencies from
  other packages do not work

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
