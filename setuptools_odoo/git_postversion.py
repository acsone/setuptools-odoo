# -*- coding: utf-8 -*-
# Copyright © 2015-2018 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import os
import subprocess

from pkg_resources import parse_version

from .manifest import MANIFEST_NAMES, NoManifestFound, parse_manifest, read_manifest

STRATEGY_NONE = "none"
STRATEGY_99_DEVN = ".99.devN"
STRATEGY_P1_DEVN = "+1.devN"
STRATEGY_DOT_N = ".N"


def _run_git_command_exit_code(args, cwd=None, stderr=None):
    return subprocess.call(["git"] + args, cwd=cwd, stderr=stderr)


def _run_git_command_bytes(args, cwd=None, stderr=None):
    output = subprocess.check_output(
        ["git"] + args, cwd=cwd, universal_newlines=True, stderr=stderr
    )
    return output.strip()


def _run_git_command_lines(args, cwd=None, stderr=None):
    output = _run_git_command_bytes(args, cwd=cwd, stderr=stderr)
    return output.split("\n")


def is_git_controlled(path):
    with open(os.devnull, "w") as devnull:
        r = _run_git_command_exit_code(["rev-parse"], cwd=path, stderr=devnull)
        return r == 0


def get_git_uncommitted(path):
    r = _run_git_command_exit_code(["diff", "--quiet", "--exit-code", "."], cwd=path)
    return r != 0


def get_git_root(path):
    return _run_git_command_bytes(["rev-parse", "--show-toplevel"], cwd=path)


def git_log_iterator(path):
    """yield commits using git log -- <dir>"""
    N = 10
    count = 0
    while True:
        lines = _run_git_command_lines(
            ["log", "--oneline", "-n", str(N), "--skip", str(count), "--", "."],
            cwd=path,
        )
        for line in lines:
            sha = line.split(" ", 1)[0]
            count += 1
            yield sha
        if len(lines) < N:
            break


def read_manifest_from_sha(sha, addon_dir, git_root):
    rel_addon_dir = os.path.relpath(addon_dir, git_root)
    for manifest_name in MANIFEST_NAMES:
        manifest_path = os.path.join(rel_addon_dir, manifest_name)
        try:
            with open(os.devnull, "w") as devnull:
                s = _run_git_command_bytes(
                    ["show", sha + ":" + manifest_path], cwd=git_root, stderr=devnull
                )
        except subprocess.CalledProcessError:
            continue
        try:
            return parse_manifest(s)
        except Exception:
            # invalid manifest
            break
    raise NoManifestFound("no manifest found in {}:{}".format(sha, addon_dir))


def _bump_last(version):
    int_version = [int(i) for i in version.split(".")]
    int_version[-1] += 1
    return ".".join(str(i) for i in int_version)


def get_git_postversion(addon_dir, strategy):
    """return the addon version number, with a developmental version increment
    if there were git commits in the addon_dir after the last version change.

    If the last change to the addon correspond to the version number in the
    manifest it is used as is for the python package version. Otherwise a
    counter is incremented for each commit and resulting version number has
    the following form, depending on the strategy (N being the number of git
    commits since the version change):

    * STRATEGY_NONE: return the version in the manifest as is
    * STRATEGY_99_DEVN: [8|9].0.x.y.z.99.devN
    * STRATEGY_P1_DEVN: [series].0.x.y.(z+1).devN
    * STRATEGY_DOT_N: [series].0.x.y.z.N

    Notes:

    * pip ignores .postN  by design (https://github.com/pypa/pip/issues/2872)
    * x.y.z.devN is anterior to x.y.z

    Note: we don't put the sha1 of the commit in the version number because
    this is not PEP 440 compliant and is therefore misinterpreted by pip.
    """
    addon_dir = os.path.realpath(addon_dir)
    last_version = read_manifest(addon_dir).get("version", "0.0.0")
    if strategy == STRATEGY_NONE:
        return last_version
    last_version_parsed = parse_version(last_version)
    if not is_git_controlled(addon_dir):
        return last_version
    if get_git_uncommitted(addon_dir):
        uncommitted = True
        count = 1
    else:
        uncommitted = False
        count = 0
    last_sha = None
    git_root = get_git_root(addon_dir)
    for sha in git_log_iterator(addon_dir):
        try:
            manifest = read_manifest_from_sha(sha, addon_dir, git_root)
        except NoManifestFound:
            break
        version = manifest.get("version", "0.0.0")
        version_parsed = parse_version(version)
        if version_parsed != last_version_parsed:
            break
        if last_sha is None:
            last_sha = sha
        else:
            count += 1
    if not count:
        return last_version
    if last_sha:
        if strategy == STRATEGY_99_DEVN:
            return last_version + ".99.dev%s" % count
        elif strategy == STRATEGY_P1_DEVN:
            return _bump_last(last_version) + ".dev%s" % count
        elif strategy == STRATEGY_DOT_N:
            return last_version + ".%s" % count
        else:
            raise RuntimeError("Unknown postversion strategy: %s" % strategy)
    if uncommitted:
        return last_version + ".dev1"
    # if everything is committed, the last commit
    # must have the same version as current,
    # so last_sha must be set and we'll never reach this branch
    return last_version
