# -*- coding: utf-8 -*-
# Copyright © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import os
import setuptools
from distutils.core import DistutilsSetupError
from warnings import warn

from . import base_addons
from . import external_dependencies
from .manifest import read_manifest, is_installable_addon
from .git_postversion import get_git_postversion

LEGACY_MODE = os.environ.get('SETUPTOOLS_ODOO_LEGACY_MODE')

if LEGACY_MODE:
    warn('SETUPTOOLS_ODOO_LEGACY_MODE support will be removed in '
         'setuptools-odoo 1.1.0. Please switch to the '
         'new package naming scheme.')

ODOO_VERSION_INFO = {
    '7.0': {
        'odoo_dep': 'openerp>=7.0a,<8.0a',
        'base_addons': base_addons.openerp7,
        'addon_dep_version': '' if not LEGACY_MODE else '>=7.0a,<8.0a',
        'pkg_name_pfx': ('openerp7-addon-'
                         if not LEGACY_MODE else 'openerp-addon-'),
        'addons_ns': 'openerp_addons',
    },
    '8.0': {
        'odoo_dep': 'odoo>=8.0a,<9.0a',
        'base_addons': base_addons.odoo8,
        'addon_dep_version': '' if not LEGACY_MODE else '>=8.0a,<9.0a',
        'pkg_name_pfx': ('odoo8-addon-'
                         if not LEGACY_MODE else 'odoo-addon-'),
        'addons_ns': 'odoo_addons',
    },
    '9.0': {
        'odoo_dep': 'odoo>=9.0a,<9.1a',
        'base_addons': base_addons.odoo9,
        'addon_dep_version': '' if not LEGACY_MODE else '>=9.0a,<9.1a',
        'pkg_name_pfx': ('odoo9-addon-'
                         if not LEGACY_MODE else 'odoo-addon-'),
        'addons_ns': 'odoo_addons',
    },
    '10.0': {
        'odoo_dep': 'odoo>=10.0,<10.1dev',
        'base_addons': base_addons.odoo10,
        'addon_dep_version': '',
        'pkg_name_pfx': 'odoo10-addon-',
        'addons_ns': 'odoo.addons',
    },
}


def _get_version(addon_dir, manifest, odoo_version_override=None,
                 git_post_version=True):
    version = manifest.get('version')
    if not version:
        warn("No version in manifest in %s" % addon_dir)
        version = '0.0.0'
    if not odoo_version_override:
        if len(version.split('.')) < 5:
            raise DistutilsSetupError("Version in manifest must have at least "
                                      "5 components and start with "
                                      "the Odoo series number in %s" %
                                      addon_dir)
        odoo_version = '.'.join(version.split('.')[:2])
    else:
        odoo_version = odoo_version_override
    if odoo_version not in ODOO_VERSION_INFO:
        raise DistutilsSetupError("Unsupported odoo version '%s' in %s" %
                                  (odoo_version, addon_dir))
    odoo_version_info = ODOO_VERSION_INFO[odoo_version]
    if git_post_version:
        version = get_git_postversion(addon_dir)
    if LEGACY_MODE and not version.startswith(odoo_version + '.'):
        version = odoo_version + '.' + version
    return version, odoo_version_info


def _get_description(addon_dir, manifest):
    return manifest.get('summary', '').strip() or manifest.get('name').strip()


def _get_long_description(addon_dir, manifest):
    readme_path = os.path.join(addon_dir, 'README.rst')
    if os.path.exists(readme_path):
        return open(readme_path).read()
    else:
        return manifest.get('description')


def _get_author(manifest):
    return manifest.get('author')


def _get_author_email(manifest):
    author = _get_author(manifest)
    if author and 'Odoo Community Association (OCA)' in author:
        return 'support@odoo-community.org'


def make_pkg_name(odoo_version_info, addon_name, with_version):
    name = odoo_version_info['pkg_name_pfx'] + addon_name
    if with_version:
        name += odoo_version_info['addon_dep_version']
    return name


def make_pkg_requirement(addon_dir, odoo_version_override=None):
    manifest = read_manifest(addon_dir)
    addon_name = os.path.basename(addon_dir)
    _, odoo_version_info = _get_version(addon_dir,
                                        manifest,
                                        odoo_version_override,
                                        git_post_version=False)
    return make_pkg_name(odoo_version_info, addon_name, True)


def _get_install_requires(odoo_version_info,
                          manifest,
                          no_depends=[],
                          depends_override={},
                          external_dependencies_override={}):
    install_requires = []
    # dependency on Odoo
    odoo_dep = odoo_version_info['odoo_dep']
    if odoo_dep:
        install_requires.append(odoo_dep)
    # dependencies on other addons (except Odoo official addons)
    for depend in manifest.get('depends', []):
        if depend in odoo_version_info['base_addons']:
            continue
        if depend in no_depends:
            continue
        if depend in depends_override:
            install_require = depends_override[depend]
        else:
            install_require = make_pkg_name(odoo_version_info, depend, True)
        if install_require:
            install_requires.append(install_require)
    # python external_dependencies
    for dep in manifest.get('external_dependencies', {}).get('python', []):
        if dep in external_dependencies_override.get('python', {}):
            dep = external_dependencies_override.get('python', {})[dep]
        else:
            dep = external_dependencies.EXTERNAL_DEPENDENCIES_MAP.get(dep, dep)
        install_requires.append(dep)
    return sorted(install_requires)


def get_install_requires_odoo_addon(addon_dir,
                                    no_depends=[],
                                    depends_override={},
                                    external_dependencies_override={},
                                    odoo_version_override=None):
    """ Get the list of requirements for an addon """
    manifest = read_manifest(addon_dir)
    _, odoo_version_info = _get_version(addon_dir,
                                        manifest,
                                        odoo_version_override,
                                        git_post_version=False)
    return _get_install_requires(odoo_version_info,
                                 manifest,
                                 no_depends,
                                 depends_override,
                                 external_dependencies_override)


def get_install_requires_odoo_addons(addons_dir,
                                     depends_override={},
                                     external_dependencies_override={},
                                     odoo_version_override=None):
    """ Get the list of requirements for a directory containing addons """
    addon_dirs = []
    addons = os.listdir(addons_dir)
    for addon in addons:
        addon_dir = os.path.join(addons_dir, addon)
        if is_installable_addon(addon_dir):
            addon_dirs.append(addon_dir)
    install_requires = set()
    for addon_dir in addon_dirs:
        r = get_install_requires_odoo_addon(
            addon_dir,
            no_depends=addons,
            depends_override=depends_override,
            external_dependencies_override=external_dependencies_override,
            odoo_version_override=odoo_version_override,
        )
        install_requires.update(r)
    return sorted(install_requires)


def _ns_to_namespace_packages(ns):
    res = []
    for part in ns.split('.'):
        if res:
            res.append(res[-1] + '.' + part)
        else:
            res.append(part)
    return res


def _find_addons_dir():
    """ Try to find the addons dir / namespace package

    Returns addons_dir, addons_ns
    """
    res = set()
    for odoo_version_info in ODOO_VERSION_INFO.values():
        addons_ns = odoo_version_info['addons_ns']
        addons_dir = os.path.join(*addons_ns.split('.'))
        if os.path.isfile(os.path.join(addons_dir, '__init__.py')):
            res.add((addons_dir, addons_ns))
    if len(res) == 0:
        raise RuntimeError("No addons namespace found.")
    if len(res) > 1:
        raise RuntimeError("More than one addons namespace found.")
    return res.pop()


def prepare_odoo_addon(depends_override={},
                       external_dependencies_override={},
                       odoo_version_override=None):
    addons_dir, addons_ns = _find_addons_dir()
    potential_addons = os.listdir(addons_dir)
    # list installable addons, except auto-installable ones
    # in case we want to combine an addon and it's glue modules
    # in a package named after the main addon
    addons = [a for a in potential_addons
              if is_installable_addon(os.path.join(addons_dir, a),
                                      unless_auto_installable=True)]
    if len(addons) == 0:
        # if no addon is found, it may mean we are trying to package
        # a single module that is marked auto-install, so let's try
        # listing all installable modules
        addons = [a for a in potential_addons
                  if is_installable_addon(os.path.join(addons_dir, a))]
    if len(addons) != 1:
        raise DistutilsSetupError('%s must contain exactly one '
                                  'installable Odoo addon dir, found %s' %
                                  (os.path.abspath(addons_dir), addons))
    addon_name = addons[0]
    addon_dir = os.path.join(addons_dir, addon_name)
    manifest = read_manifest(addon_dir)
    version, odoo_version_info = _get_version(addon_dir,
                                              manifest,
                                              odoo_version_override,
                                              git_post_version=True)
    install_requires = get_install_requires_odoo_addon(
        addon_dir,
        depends_override=depends_override,
        external_dependencies_override=external_dependencies_override,
        odoo_version_override=odoo_version_override,
    )
    setup_keywords = {
        'name': make_pkg_name(odoo_version_info, addon_name, False),
        'version': version,
        'description': _get_description(addon_dir, manifest),
        'long_description': _get_long_description(addon_dir, manifest),
        'url': manifest.get('website'),
        'license': manifest.get('license'),
        'packages': setuptools.find_packages(),
        'include_package_data': True,
        'namespace_packages': _ns_to_namespace_packages(addons_ns),
        'zip_safe': False,
        'install_requires': install_requires,
        'author': _get_author(manifest),
        'author_email': _get_author_email(manifest),
        # TODO: keywords, classifiers
    }
    # import pprint; pprint.pprint(setup_keywords)
    return {k: v for k, v in setup_keywords.items() if v is not None}


def prepare_odoo_addons(depends_override={},
                        external_dependencies_override={},
                        odoo_version_override=None):
    addons_dir, addons_ns = _find_addons_dir()
    install_requires = get_install_requires_odoo_addons(
        addons_dir,
        depends_override=depends_override,
        external_dependencies_override=external_dependencies_override,
        odoo_version_override=odoo_version_override,
    )
    setup_keywords = {
        'packages': setuptools.find_packages(),
        'include_package_data': True,
        'namespace_packages': _ns_to_namespace_packages(addons_ns),
        'zip_safe': False,
        'install_requires': install_requires,
    }
    # import pprint; pprint.pprint(setup_keywords)
    return {k: v for k, v in setup_keywords.items() if v is not None}
