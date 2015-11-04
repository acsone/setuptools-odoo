# -*- coding: utf-8 -*-
# © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import ast
import inspect
import os
import setuptools


ODOO_VERSION_INFO = {
    '8.0': {
        'name_prefix': 'odoo-addon',
        'odoo_dep': 'odoo>=8.<9',
        'default_namespace': 'odoo_addons',
    },
    '9.0': {
        'name_prefix': 'odoo-addon',
        'odoo_dep': 'odoo>=9.<10',
        'default_namespace': 'odoo_addons',
    },
}


def _make_src(addon_dir, addon_name, namespace='openerp.addons', src_dir='src'):
    """ create a 'src' directory containing the canonical module
    structure in it's namespace package, symlinking to the module directory

    This is to make sure namespace packages are declared properly
    and 'setup.py develop' works, working around
    https://bitbucket.org/pypa/setuptools/issues/230

    If you structure the addon source code according to the real package
    structure (eg openerp/addons/modulename, odoo_addons/modulename),
    this is not necessary.
    """
    namespace_dirs = namespace.split('.')
    # declare namespace packages
    # this works in combination with https://github.com/odoo/odoo/pull/8758
    # if namespace is 'openerp.addons' or in combination with XXX if namespace
    # is 'odoo_addons'
    full_namespace_dir = os.path.join(addon_dir, src_dir)
    for namespace_dir in namespace_dirs:
        full_namespace_dir = os.path.join(full_namespace_dir, namespace_dir)
        if not os.path.isdir(full_namespace_dir):
            os.makedirs(full_namespace_dir)
        open(os.path.join(full_namespace_dir, '__init__.py'), 'w').\
            write("__import__('pkg_resources').declare_namespace(__name__)\n")
    # symlink to the main module directory so we have a canonical structure:
    # namespace/addon_name/...
    module_link = os.path.join(full_namespace_dir, addon_name)
    if not os.path.exists(module_link):
        os.symlink(os.path.relpath(addon_dir, full_namespace_dir), module_link)


def _read_manifest(addon_dir):
    for manifest_name in ('__odoo__.py', '__openerp__.py', '__terp__.py'):
        manifest_path = os.path.join(addon_dir, manifest_name)
        if os.path.isfile(manifest_path):
            return ast.literal_eval(open(manifest_path).read())
    raise RuntimeError("no Odoo manifest found")


def _get_version(manifest):
    version = manifest.get('version')
    if not version:
        raise RuntimeError("No version in manifest")
    if len(version.split('.')) < 5:
        raise RuntimeError("Version in manifest must have at least "
                           "5 components and start with the Odoo series number")
    odoo_version = '.'.join(version.split('.')[:2])
    if odoo_version not in ODOO_VERSION_INFO:
        raise RuntimeError("Unsupported odoo version '%s'" % odoo_version)
    return version, odoo_version


def _get_description(manifest):
    return manifest.get('summary', '').strip() or manifest.get('name').strip()


def _get_long_description(addon_dir, manifest):
    readme_path = os.path.join(addon_dir, 'README.rst')
    if os.path.exists(readme_path):
        return open(readme_path).read()
    else:
        return manifest.get('description')


def prepare(addon_dir=None, addon_name=None,
            namespace=None, src_dir='src',
            make_src=True):
    """ prepare setuptools.setup() keyword arguments for an odoo addon

    Most setup metadata is obtained from the __openerp__.py manifest.
    """
    if not addon_dir:
        # find addon directory from caller module (normally setup.py)
        caller_module = inspect.getmodule(inspect.stack()[1][0])
        addon_dir = os.path.dirname(os.path.abspath(caller_module.__file__))
    if not addon_name:
        addon_name = os.path.basename(os.path.abspath(addon_dir))
    addon_fullname = 'openerp.addons.' + addon_name
    manifest = _read_manifest(addon_dir)
    version, odoo_version = _get_version(manifest)
    odoo_version_info = ODOO_VERSION_INFO[odoo_version]
    name_prefix = odoo_version_info['name_prefix']
    if not namespace:
        namespace = odoo_version_info['default_namespace']
    if make_src:
        _make_src(addon_dir, addon_name, namespace, src_dir)
    return {
        'name': name_prefix + '-' + addon_name,
        'version': version,
        'description': _get_description(manifest),
        'long_description': _get_long_description(addon_dir, manifest),
        'url': manifest.get('website'),
        'license': manifest.get('license'),
        'packages': setuptools.find_packages(os.path.join(addon_dir, src_dir)),
        'package_dir': {'': src_dir},
        'package_data': {addon_fullname: ['static/description/*']},  # TODO
        'namespace_packages': [namespace],  # TODO parent namespaces
        'zip_safe': False,
        # TODO: keywords, classifiers, authors, install_requires
    }
