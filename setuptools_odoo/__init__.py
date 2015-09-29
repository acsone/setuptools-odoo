# -*- coding: utf-8 -*-
# © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import ast
import inspect
import os
import setuptools


ODOO_VERSION_INFO = {
    '8.0': {
        'name_prefix': 'odoo8',
        'odoo_dep': 'odoo>=8.<9',
    },
    '9.0': {
        'name_prefix': 'odoo9',
        'odoo_dep': 'odoo>=9.<10',
    },
}


def _make_src(addon_dir, addon_name, src_dir='src'):
    """ create a 'src' directory containing the canonical module
    structure, symlinking to the module directory

    This is to make sure namespace packages are declared properly
    and 'setup.py develop' works, working around
    https://bitbucket.org/pypa/setuptools/issues/230

    If you structure the addon source code according to the real
    package structure openerp/addons/modulename, this is
    not necessary.
    """
    openerp_dir = os.path.join(addon_dir, src_dir, 'openerp')
    addons_dir = os.path.join(openerp_dir, 'addons')
    module_link = os.path.join(addons_dir, addon_name)
    if not os.path.isdir(addons_dir):
        os.makedirs(addons_dir)
    open(os.path.join(openerp_dir, '__init__.py'), 'w').\
        write("__import__('pkg_resources').declare_namespace(__name__)\n")
    open(os.path.join(addons_dir, '__init__.py'), 'w').\
        write("__import__('pkg_resources').declare_namespace(__name__)\n")
    if not os.path.exists(module_link):
        os.symlink(os.path.relpath(addon_dir, addons_dir), module_link)


def _get_description(addon_dir, manifest):
    return manifest.get('summary', '').strip() or manifest.get('name')


def _get_long_description(addon_dir, manifest):
    readme_path = os.path.join(addon_dir, 'README.rst')
    if os.path.exists(readme_path):
        return open(readme_path).read()
    else:
        return manifest.get('description')


def prepare(odoo_version=None,
            addon_dir=None, addon_name=None,
            src_dir='src', make_src=True):
    if not addon_dir:
        # find addon directory from caller module (normally setup.py)
        caller_module = inspect.getmodule(inspect.stack()[1][0])
        addon_dir = os.path.dirname(os.path.abspath(caller_module.__file__))
    if not addon_name:
        addon_name = os.path.basename(os.path.abspath(addon_dir))
    addon_fullname = 'openerp.addons.' + addon_name
    manifest_path = os.path.join(addon_dir, '__openerp__.py')
    manifest = ast.literal_eval(open(manifest_path).read())
    if not odoo_version:
        odoo_version = manifest.get('version', '')[:3]
    if odoo_version not in ODOO_VERSION_INFO:
        raise RuntimeError("Unsupported Odoo version '%s'" % odoo_version)
    odoo_version_info = ODOO_VERSION_INFO[odoo_version]
    name_prefix = odoo_version_info['name_prefix']
    if make_src:
        _make_src(addon_dir, addon_name, src_dir)
    return {
        'name': name_prefix + '-' + addon_name,
        'version': manifest.get('version'),
        'description': _get_description(addon_dir, manifest),
        'long_description': _get_long_description(addon_dir, manifest),
        'url': manifest.get('website'),
        'license': manifest.get('license'),
        'packages': setuptools.find_packages(os.path.join(addon_dir, src_dir)),
        'package_dir': {'': src_dir},
        'package_data': {addon_fullname: ['static/description/*']},  # TODO
        'namespace_packages': ['openerp', 'openerp.addons'],
        'zip_safe': False,
        # TODO: keywords, classifiers, authors, install_requires
    }
