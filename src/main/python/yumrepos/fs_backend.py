#!/usr/bin/env python
from __future__ import print_function
from distutils.spawn import find_executable
from fnmatch import fnmatch
import glob
import os
import shutil
import subprocess
import sys

try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache

from werkzeug import secure_filename


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


def remove(fname):
    if os.path.exists(fname):
        os.remove(fname)


def mark_as_added(filename):
    unmark_as_deleted(filename)
    touch(filename + ".added")


def unmark_as_added(filename):
    remove(filename + ".added")


def mark_as_deleted(filename):
    unmark_as_added(filename)
    touch(filename + ".removed")


def unmark_as_deleted(filename):
    try:
        remove(filename + ".removed")
    except FileNotFoundError:
        pass


def check_output_backported(*popenargs, **kwargs):
    r"""Run command with arguments and return its output as a byte string.
    Backported from Python 2.7 as it's implemented as pure python on stdlib.
    >>> check_output(['/usr/bin/python', '--version'])
    Python 2.6.2

    blatantly copied from https://gist.github.com/edufelipe/1027906
    """
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        error = subprocess.CalledProcessError(retcode, cmd)
        error.output = output
        raise error
    return output


if "check_output" not in dir(subprocess):
    subprocess.check_output = check_output_backported


class FsBackend(object):
    def __init__(self, repos_folder, createrepo_bins=['createrepo_c', 'createrepo']):
        self.repos_folder = os.path.abspath(repos_folder)
        self.createrepo_bin = 'touch'   # simplest fallback
        for createrepo_bin in createrepo_bins:
            if find_executable(createrepo_bin):
                self.createrepo_bin = createrepo_bin
                break

        try:
            os.mkdir(self.repos_folder)
        except OSError as e:
            if e.errno != 17:
                raise

    # repo stuff

    def create_repo_metadata(self, reponame):
        print("creating metadata for %s" % reponame)
        with open(os.devnull, "w") as fnull:
            subprocess.check_call([self.createrepo_bin,
                                   "--update",
                                   os.path.join(self.repos_folder, reponame)],
                                  stdout=fnull,
                                  stderr=fnull)

    def create_repo(self, reponame):
        try:
            # print >> sys.stderr, "trying to create_repo %s" % self._to_path(reponame)
            os.mkdir(self._to_path(reponame))
        except OSError as e:
            print(e)
            if e.errno != 17:
                raise
        print("repo %s created!" % reponame)
        self.create_repo_metadata(reponame)
        return ('', 201)

    def remove_repo(self, reponame, recursivly=False):
        repopath = self._to_path(reponame)
        if not os.path.exists(repopath):
            return ('', 404)
        if not recursivly:
            if len(glob.glob(os.path.join(repopath, "*.rpm"))) > 0:
                return "repo not empty, aborting", 409
        try:
            shutil.rmtree(repopath)
        except OSError as e:
            if e.errno == 39:
                return ('', 409)
            raise
        return ('', 204)

    # repo link stuff

    def create_repo_link(self, reponame, link_to):
        if self.exists(reponame):
            os.remove(self._to_path(reponame))
        os.symlink(link_to, self._to_path(reponame))
        return ('', 201)

    def remove_repo_link(self, reponame):
        if not self.exists(reponame):
            return ('', 404)
        os.remove(self._to_path(reponame))
        return ('', 204)

    # rpm stuff

    def upload_rpm(self, reponame, file):
        filename = secure_filename(file.filename)
        complete_filename = self._to_path(reponame, filename)
        if os.path.exists(complete_filename):
            return "%s already exists" % filename, 409
        try:
            mark_as_added(complete_filename)
            file.save(complete_filename)
            return ('', 201)
        except IOError as e:
            if e.errno == 2:
                return ('', 404)

    def _to_path(self, reponame, rpmname=None):
        if rpmname:
            return os.path.join(self.repos_folder, reponame, rpmname)
        return os.path.join(self.repos_folder, reponame)

    def exists(self, reponame, rpmname=''):
        path = self._to_path(reponame, rpmname)
        return os.path.islink(path) or os.path.exists(path)

    def isfile(self, path):
        filename = self._to_path(path)
        return os.path.isfile(filename) and os.path.exists(filename)

    def stage(self, source, rpm, target):
        shutil.move(self._to_path(source, rpm), self._to_path(target, rpm))
        self.create_repo_metadata(source)
        self.create_repo_metadata(target)
        return '', 201

    def remove_rpm(self, reponame, rpmname):
        filename = self._to_path(reponame, rpmname)
        if not os.path.exists(filename):
            return ('', 404)
        mark_as_deleted(filename)
        return ('', 204)

    def is_link(self, reponame):
        return os.path.islink(self._to_path(reponame))

    @lru_cache()
    def get_rpm_info(self, reponame, rpmname):
        filename = self._to_path(reponame, rpmname)
        try:
            output = subprocess.check_output(["rpm", "-qpi", filename])
        except Exception as e:
            print(e)
            raise
        return output

    def list_repos(self):
        return os.listdir(self.repos_folder)

    def list_rpms(self, reponame):
        return [file for file in os.listdir(self._to_path(reponame))
                if fnmatch(file, '*.rpm')]

    def get_filename(self, reponame, path=None):
        return self._to_path(reponame, path)

    def walk_repos(self):
        for dirpath, dirnames, filenames in os.walk(self.repos_folder):
            dirnames[:] = [d for d in dirnames if d != "repodata"]
            yield dirpath.replace(self.repos_folder, '.')

    def update_all_metadata(self):
        self.commit_actions()
        for reponame in self.walk_repos():
            self.create_repo_metadata(reponame)

    def commit_actions(self):
        for dirpath, dirnames, filenames in os.walk(self.repos_folder):
            dirnames[:] = [d for d in dirnames if d != "repodata"]
            for filename in filenames:
                filename, action = self.split_action(filename)
                if not action:
                    continue
                full_path = os.path.join(dirpath, filename)
                if action == "removed":
                    os.unlink(full_path)
                    unmark_as_deleted(full_path)
                if action == "added":
                    unmark_as_added(full_path)

    def split_action(self, full_filename):
        if full_filename.endswith("added") or full_filename.endswith("removed"):
            return full_filename.rsplit(".", 1)
        return (full_filename, None)
