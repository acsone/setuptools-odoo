# -*- coding: utf-8 -*-
# Copyright © 2015-2018 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import email.parser
import io
import os
from distutils.core import DistutilsSetupError
from warnings import warn

import setuptools

from . import base_addons
from . import external_dependencies
from .manifest import read_manifest, is_installable_addon
from .git_postversion import get_git_postversion

ODOO_VERSION_INFO = {
    '7.0': {
        'odoo_dep': 'openerp>=7.0a,<8.0a',
        'base_addons': base_addons.openerp7,
        'pkg_name_pfx': 'openerp7-addon-',
        'addons_ns': 'openerp_addons',
        'namespace_packages': ['openerp_addons'],
        'python_requires': '~=2.7',
        'universal_wheel': False,
    },
    '8.0': {
        'odoo_dep': 'odoo>=8.0a,<9.0a',
        'base_addons': base_addons.odoo8,
        'pkg_name_pfx': 'odoo8-addon-',
        'addons_ns': 'odoo_addons',
        'namespace_packages': ['odoo_addons'],
        'python_requires': '~=2.7',
        'universal_wheel': False,
    },
    '9.0': {
        'odoo_dep': 'odoo>=9.0a,<9.1a',
        'base_addons': base_addons.odoo9,
        'pkg_name_pfx': 'odoo9-addon-',
        'addons_ns': 'odoo_addons',
        'namespace_packages': ['odoo_addons'],
        'python_requires': '~=2.7',
        'universal_wheel': False,
    },
    '10.0': {
        'odoo_dep': 'odoo>=10.0,<10.1dev',
        'base_addons': base_addons.odoo10,
        'pkg_name_pfx': 'odoo10-addon-',
        'addons_ns': 'odoo.addons',
        'namespace_packages': ['odoo', 'odoo.addons'],
        'python_requires': '~=2.7',
        'universal_wheel': False,
    },
    '11.0': {
        'odoo_dep': 'odoo>=11.0a,<11.1dev',
        'base_addons': base_addons.odoo11,
        'pkg_name_pfx': 'odoo11-addon-',
        'addons_ns': 'odoo.addons',
        'namespace_packages': None,
        'python_requires': ', '.join([
            '>=2.7', '!=3.0.*', '!=3.1.*', '!=3.2.*', '!=3.3.*', '!=3.4.*'
        ]),
        'universal_wheel': True,
    },
    '12.0': {
        'odoo_dep': 'odoo>=12.0a,<12.1dev',
        'base_addons': base_addons.odoo12,
        'pkg_name_pfx': 'odoo12-addon-',
        'addons_ns': 'odoo.addons',
        'namespace_packages': None,
        'python_requires': '>=3.5',
        'universal_wheel': False,
    },
}


def _get_odoo_version_info(addons_dir, odoo_version_override=None):
    """ Detect Odoo version from an addons directory """
    odoo_version_info = None
    addons = os.listdir(addons_dir)
    for addon in addons:
        addon_dir = os.path.join(addons_dir, addon)
        if is_installable_addon(addon_dir):
            manifest = read_manifest(addon_dir)
            _, _, addon_odoo_version_info = _get_version(
                addon_dir, manifest, odoo_version_override,
                git_post_version=False)
            if odoo_version_info is not None and \
                    odoo_version_info != addon_odoo_version_info:
                raise DistutilsSetupError("Not all addons are for the same "
                                          "odoo version in %s (error detected "
                                          "in %s)" % (addons_dir, addon))
            odoo_version_info = addon_odoo_version_info
    return odoo_version_info


def _get_version(addon_dir, manifest, odoo_version_override=None,
                 git_post_version=True):
    """ Get addon version information from an addon directory """
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
    return version, odoo_version, odoo_version_info


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


def make_pkg_name(odoo_version_info, addon_name):
    name = odoo_version_info['pkg_name_pfx'] + addon_name
    return name


def make_pkg_requirement(addon_dir, odoo_version_override=None):
    manifest = read_manifest(addon_dir)
    addon_name = os.path.basename(addon_dir)
    _, _, odoo_version_info = _get_version(addon_dir,
                                           manifest,
                                           odoo_version_override,
                                           git_post_version=False)
    return make_pkg_name(odoo_version_info, addon_name)


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
            install_require = make_pkg_name(odoo_version_info, depend)
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
    _, _, odoo_version_info = _get_version(addon_dir,
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


def _find_addons_dir():
    """ Try to find the addons dir / namespace package

    Returns addons_dir, addons_ns
    """
    res = set()
    for odoo_version_info in ODOO_VERSION_INFO.values():
        addons_ns = odoo_version_info['addons_ns']
        addons_dir = os.path.join(*addons_ns.split('.'))
        if os.path.isdir(addons_dir):
            if not odoo_version_info['namespace_packages'] or \
                    os.path.isfile(os.path.join(addons_dir, '__init__.py')):
                res.add((addons_dir, addons_ns))
    if len(res) == 0:
        raise RuntimeError("No addons namespace found.")
    if len(res) > 1:
        raise RuntimeError("More than one addons namespace found.")
    return res.pop()


def _make_classifiers(manifest):
    classifiers = [
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
    # commonly used licenses in OCA
    LICENSES = {
        'agpl-3':
            'License :: OSI Approved :: '
            'GNU Affero General Public License v3',
        'agpl-3 or any later version':
            'License :: OSI Approved :: '
            'GNU Affero General Public License v3 or later (AGPLv3+)',
        'gpl-2':
            'License :: OSI Approved :: '
            'GNU General Public License v2 (GPLv2)',
        'gpl-2 or any later version':
            'License :: OSI Approved :: '
            'GNU General Public License v2 or later (GPLv2+)',
        'gpl-3':
            'License :: OSI Approved :: '
            'GNU General Public License v3 (GPLv3)',
        'gpl-3 or any later version':
            'License :: OSI Approved :: '
            'GNU General Public License v3 or later (GPLv3+)',
        'lgpl-2':
            'License :: OSI Approved :: '
            'GNU Lesser General Public License v2 (LGPLv2)',
        'lgpl-2 or any later version':
            'License :: OSI Approved :: '
            'GNU Lesser General Public License v2 or later (LGPLv2+)',
        'lgpl-3':
            'License :: OSI Approved :: '
            'GNU Lesser General Public License v3 (LGPLv3)',
        'lgpl-3 or any later version':
            'License :: OSI Approved :: '
            'GNU Lesser General Public License v3 or later (LGPLv3+)',
    }
    license = manifest.get('license')
    if license:
        license_classifier = LICENSES.get(license.lower())
        if license_classifier:
            classifiers.append(license_classifier)
    return classifiers


def _setuptools_find_packages(odoo_version_info):
    # setuptools.find_package() does not find namespace packages
    # without __init__.py, apparently, so work around that
    pkg = setuptools.find_packages()
    if odoo_version_info['addons_ns'] not in pkg:
        pkg.append(odoo_version_info['addons_ns'])
    return pkg


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
    if os.path.exists('PKG-INFO'):
        with io.open('PKG-INFO', encoding='utf-8') as fp:
            pkg_info = email.parser.HeaderParser().parse(fp)
            version = pkg_info['Version']
        _, _, odoo_version_info = _get_version(
            addon_dir, manifest, odoo_version_override, git_post_version=False)
    else:
        version, _, odoo_version_info = _get_version(
            addon_dir, manifest, odoo_version_override, git_post_version=True)
    install_requires = get_install_requires_odoo_addon(
        addon_dir,
        depends_override=depends_override,
        external_dependencies_override=external_dependencies_override,
        odoo_version_override=odoo_version_override,
    )
    setup_keywords = {
        'name': make_pkg_name(odoo_version_info, addon_name),
        'version': version,
        'description': _get_description(addon_dir, manifest),
        'long_description': _get_long_description(addon_dir, manifest),
        'url': manifest.get('website'),
        'license': manifest.get('license'),
        'packages': _setuptools_find_packages(odoo_version_info),
        'include_package_data': True,
        'namespace_packages': odoo_version_info['namespace_packages'],
        'zip_safe': False,
        'install_requires': install_requires,
        'python_requires': odoo_version_info['python_requires'],
        'author': _get_author(manifest),
        'author_email': _get_author_email(manifest),
        'classifiers': _make_classifiers(manifest)
        # TODO: more classifiers: development status, ...
        # TODO: keywords
    }
    # import pprint; pprint.pprint(setup_keywords)
    return {k: v for k, v in setup_keywords.items() if v is not None}


def prepare_odoo_addons(depends_override={},
                        external_dependencies_override={},
                        odoo_version_override=None):
    addons_dir, addons_ns = _find_addons_dir()
    odoo_version_info = _get_odoo_version_info(
        addons_dir, odoo_version_override)
    install_requires = get_install_requires_odoo_addons(
        addons_dir,
        depends_override=depends_override,
        external_dependencies_override=external_dependencies_override,
        odoo_version_override=odoo_version_override,
    )
    setup_keywords = {
        'packages': _setuptools_find_packages(odoo_version_info),
        'include_package_data': True,
        'namespace_packages': odoo_version_info['namespace_packages'],
        'zip_safe': False,
        'install_requires': install_requires,
        'python_requires': odoo_version_info['python_requires'],
    }
    # import pprint; pprint.pprint(setup_keywords)
    return {k: v for k, v in setup_keywords.items() if v is not None}
