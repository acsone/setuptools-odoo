# -*- coding: utf-8 -*-
# © 2015 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import os
import setuptools
from distutils.core import DistutilsSetupError
from warnings import warn

from . import base_addons
from . import external_dependencies
from .manifest import read_manifest, is_installable_addon
from .git_postversion import get_git_postversion


ADDON_PKG_NAME_PREFIX = 'odoo-addon-'

ADDONS_NAMESPACE = 'odoo_addons'

ODOO_VERSION_INFO = {
    '8.0': {
        'odoo_dep': 'odoo>=8.0a,<9.0a',
        'base_addons': base_addons.odoo8,
        'addon_dep_version': '>=8.0a,<9.0a',
    },
    '9.0': {
        'odoo_dep': 'odoo>=9.0a,<9.1a',
        'base_addons': base_addons.odoo9,
        'addon_dep_version': '>=9.0a,<9.1a',
    },
}


def _get_version(addon_dir, manifest, odoo_version_override=None):
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
        if odoo_version not in ODOO_VERSION_INFO:
            raise DistutilsSetupError("Unsupported odoo version '%s' in %s" %
                                      (odoo_version, addon_dir))
    else:
        odoo_version = odoo_version_override
    odoo_version_info = ODOO_VERSION_INFO[odoo_version]
    version = get_git_postversion(addon_dir)
    return version, odoo_version_info


def _get_description(addon_dir, manifest):
    return manifest.get('summary', '').strip() or manifest.get('name').strip()


def _get_long_description(addon_dir, manifest):
    readme_path = os.path.join(addon_dir, 'README.rst')
    if os.path.exists(readme_path):
        return open(readme_path).read()
    else:
        return manifest.get('description')


def make_pkg_name(addon_name):
    return ADDON_PKG_NAME_PREFIX + addon_name


def make_pkg_requirement(addon_dir, odoo_version_override=None):
    manifest = read_manifest(addon_dir)
    addon_name = os.path.basename(addon_dir)
    version, odoo_version_info = _get_version(addon_dir,
                                              manifest,
                                              odoo_version_override)
    addon_dep_version = odoo_version_info['addon_dep_version']
    return make_pkg_name(addon_name) + addon_dep_version


def _get_install_requires(odoo_version_info,
                          manifest,
                          no_depends=[],
                          depends_override={},
                          external_dependencies_override={}):
    # dependency on Odoo
    install_requires = [odoo_version_info['odoo_dep']]
    # dependencies on other addons (except Odoo official addons)
    addon_dep_version = odoo_version_info['addon_dep_version']
    base_addons = odoo_version_info['base_addons']
    for depend in manifest.get('depends', []):
        if depend in base_addons:
            continue
        if depend in no_depends:
            continue
        if depend in depends_override:
            install_require = depends_override[depend]
        else:
            install_require = make_pkg_name(depend) + addon_dep_version
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
    version, odoo_version_info = _get_version(addon_dir,
                                              manifest,
                                              odoo_version_override)
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


def prepare_odoo_addon(depends_override={},
                       external_dependencies_override={},
                       odoo_version_override=None):
    addons_dir = ADDONS_NAMESPACE
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
                                  'installable Odoo addon dir' %
                                  os.path.abspath(addons_dir))
    addon_name = addons[0]
    addon_dir = os.path.join(ADDONS_NAMESPACE, addon_name)
    manifest = read_manifest(addon_dir)
    version, odoo_version_info = _get_version(addon_dir,
                                              manifest,
                                              odoo_version_override)
    install_requires = get_install_requires_odoo_addon(
        addon_dir,
        depends_override=depends_override,
        external_dependencies_override=external_dependencies_override,
        odoo_version_override=odoo_version_override,
    )
    setup_keywords = {
        'name': make_pkg_name(addon_name),
        'version': version,
        'description': _get_description(addon_dir, manifest),
        'long_description': _get_long_description(addon_dir, manifest),
        'url': manifest.get('website'),
        'license': manifest.get('license'),
        'packages': setuptools.find_packages(),
        'include_package_data': True,
        'namespace_packages': [ADDONS_NAMESPACE],
        'zip_safe': False,
        'install_requires': install_requires,
        # TODO: keywords, classifiers, authors
    }
    # import pprint; pprint.pprint(setup_keywords)
    return {k: v for k, v in setup_keywords.items() if v is not None}


def prepare_odoo_addons(depends_override={},
                        external_dependencies_override={},
                        odoo_version_override=None):
    addons_dir = ADDONS_NAMESPACE
    install_requires = get_install_requires_odoo_addons(
        addons_dir,
        depends_override=depends_override,
        external_dependencies_override=external_dependencies_override,
        odoo_version_override=odoo_version_override,
    )
    setup_keywords = {
        'packages': setuptools.find_packages(),
        'include_package_data': True,
        'namespace_packages': [ADDONS_NAMESPACE],
        'zip_safe': False,
        'install_requires': install_requires,
    }
    # import pprint; pprint.pprint(setup_keywords)
    return {k: v for k, v in setup_keywords.items() if v is not None}
