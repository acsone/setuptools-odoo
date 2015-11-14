# -*- coding: utf-8 -*-
# © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import ast
import inspect
import os
import setuptools

from . import base_addons
from . import external_dependencies


ODOO_VERSION_INFO = {
    '8.0': {
        'name_prefix': 'odoo-addon',
        'default_namespace': 'odoo_addons',
        'odoo_dep': 'odoo>=8,<9',
        'base_addons': base_addons.odoo8,
        'addon_dep_version': '>=8,<9',
    },
    '9.0': {
        'name_prefix': 'odoo-addon',
        'default_namespace': 'odoo_addons',
        'odoo_dep': 'odoo>=9,<10',
        'base_addons': base_addons.odoo9,
        'addon_dep_version': '>=9,<10',
    },
}


def _make_src(addon_dir, addon_name, namespace, src_dir):
    """ create a src_dir directory containing the canonical module
    structure in it's namespace package, symlinking to the addon directory

    This is to make sure namespace packages are declared properly
    and 'setup.py develop' works, working around
    https://bitbucket.org/pypa/setuptools/issues/230

    If you structure the addon source code according to the real package
    structure (ie odoo_addons/addon_name) this is not necessary.

    Caveat: this symlinked structure which include a loop confuses
    setup.py sdist and bdist, but is fine for setup.py bdist_wheel and develop,
    so this is sufficient.  If this is an issue for you, put your setup.py
    outside of the addon directory so there is no symlink loop.
    """
    namespace_dirs = namespace.split('.')
    # declare namespace packages
    # this works in combination with https://github.com/odoo/odoo/pull/8758
    # if namespace is 'openerp.addons' or in combination with the included
    # odoo-server-autodiscover script if namespace is 'odoo_addons'
    full_namespace_dir = src_dir
    for namespace_dir in namespace_dirs:
        full_namespace_dir = os.path.join(full_namespace_dir, namespace_dir)
        if not os.path.isdir(full_namespace_dir):
            os.makedirs(full_namespace_dir)
        open(os.path.join(full_namespace_dir, '__init__.py'), 'w').\
            write("__import__('pkg_resources').declare_namespace(__name__)\n")
    # symlink to the main addon directory so we have a canonical structure:
    # namespace/addon_name/...
    module_link = os.path.join(full_namespace_dir, addon_name)
    if not os.path.exists(module_link):
        os.symlink(os.path.relpath(addon_dir, full_namespace_dir), module_link)


def _read_manifest(addon_dir):
    for manifest_name in ('__odoo__.py', '__openerp__.py', '__terp__.py'):
        manifest_path = os.path.join(addon_dir, manifest_name)
        if os.path.isfile(manifest_path):
            return ast.literal_eval(open(manifest_path).read())
    raise RuntimeError("no Odoo manifest found in %s" % addon_dir)


def _get_version(addon_dir, manifest):
    version = manifest.get('version')
    if not version:
        raise RuntimeError("No version in manifest in %s" % addon_dir)
    if len(version.split('.')) < 5:
        raise RuntimeError("Version in manifest must have at least "
                           "5 components and start with "
                           "the Odoo series number in %s" % addon_dir)
    odoo_version = '.'.join(version.split('.')[:2])
    if odoo_version not in ODOO_VERSION_INFO:
        raise RuntimeError("Unsupported odoo version '%s' in %s" %
                           (odoo_version, addon_dir))
    return version, odoo_version


def _get_description(manifest):
    return manifest.get('summary', '').strip() or manifest.get('name').strip()


def _get_long_description(addon_dir, manifest):
    readme_path = os.path.join(addon_dir, 'README.rst')
    if os.path.exists(readme_path):
        return open(readme_path).read()
    else:
        return manifest.get('description')


def _get_pkg_name(odoo_version_info, name):
    name_prefix = odoo_version_info['name_prefix']
    return name_prefix + '-' + name


def _get_install_requires(odoo_version_info, manifest):
    # dependency on Odoo
    install_requires = [odoo_version_info['odoo_dep']]
    # dependencies on other addons (except Odoo official addons)
    addon_dep_version = odoo_version_info['addon_dep_version']
    base_addons = odoo_version_info['base_addons']
    for depend in manifest.get('depends', []):
        if depend in base_addons:
            continue
        install_require = _get_pkg_name(odoo_version_info, depend) + \
            addon_dep_version
        install_requires.append(install_require)
    # python external_dependencies
    for dep in manifest.get('external_dependencies', {}).get('python', []):
        dep = external_dependencies.EXTERNAL_DEPENDENCIES_MAP.get(dep, dep)
        install_requires.append(dep)
    return install_requires


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
    manifest = _read_manifest(addon_dir)
    version, odoo_version = _get_version(addon_dir, manifest)
    odoo_version_info = ODOO_VERSION_INFO[odoo_version]
    if not namespace:
        namespace = odoo_version_info['default_namespace']
    addon_fullname = namespace + '.' + addon_name
    if make_src:
        _make_src(addon_dir, addon_name, namespace, src_dir)
    setup_keywords = {
        'name': _get_pkg_name(odoo_version_info, addon_name),
        'version': version,
        'description': _get_description(manifest),
        'long_description': _get_long_description(addon_dir, manifest),
        'url': manifest.get('website'),
        'license': manifest.get('license'),
        'packages': setuptools.find_packages(src_dir),
        'package_dir': {'': src_dir},
        'include_package_data': True,
        'exclude_package_data': {addon_fullname: [src_dir+'/*']},
        'namespace_packages': [namespace],  # TODO parent namespaces
        'zip_safe': False,
        'install_requires': _get_install_requires(odoo_version_info, manifest),
        # TODO: keywords, classifiers, authors
    }
    # import pprint; pprint.pprint(setup_keywords)
    return setup_keywords
