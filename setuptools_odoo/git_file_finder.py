# -*- coding: utf-8 -*-
# Copyright © 2018 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

import os
import subprocess


def _git_toplevel(path):
    try:
        out = subprocess.check_output([
            'git', 'rev-parse', '--show-toplevel',
        ], cwd=(path or '.'), universal_newlines=True)
        return os.path.realpath(out.strip())
    except subprocess.CalledProcessError:
        return None


def _git_ls_files_and_dirs(toplevel):
    out = subprocess.check_output([
        'git', 'ls-files',
    ], cwd=toplevel, universal_newlines=True)
    git_files = {os.path.join(toplevel, f) for f in out.split()}
    git_dirs = set()
    for git_file in git_files:
        dirname = os.path.dirname(git_file)
        while True:
            if len(dirname) < len(toplevel):
                break
            if dirname in git_dirs:
                break
            git_dirs.add(dirname)
            dirname = os.path.dirname(dirname)
    return git_files, git_dirs


def find_files(path=''):
    """ setuptools compatible git file finder that follows symlinks

    Spec here: http://setuptools.readthedocs.io/en/latest/setuptools.html#\
        adding-support-for-revision-control-systems
    """
    toplevel = _git_toplevel(path)
    if not toplevel:
        return []
    git_files, git_dirs = _git_ls_files_and_dirs(toplevel)
    realpath = os.path.realpath(path)
    assert realpath.startswith(toplevel)
    assert realpath in git_dirs
    seen = set()
    res = []
    for dirpath, dirnames, filenames in os.walk(realpath, followlinks=True):
        realdirpath = os.path.realpath(dirpath)  # resolve symlink
        if realdirpath not in git_dirs or realdirpath in seen:
            dirnames[:] = []
            continue
        for filename in filenames:
            fullfilename = os.path.join(dirpath, filename)  # with symlink
            if os.path.realpath(fullfilename) in git_files:
                res.append(
                    os.path.join(path, os.path.relpath(fullfilename, path)))
        seen.add(realdirpath)
    return res
