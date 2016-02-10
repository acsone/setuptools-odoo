Changes
~~~~~~~

1.0.0b3 (unreleased)
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
