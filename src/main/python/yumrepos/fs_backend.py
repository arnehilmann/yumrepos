#!/usr/bin/env python
from distutils.spawn import find_executable
from fnmatch import fnmatch
import glob
import os
import shutil
import subprocess

try:
    from functools import lru_cache
except ImportError:
    from yumrepos.backports.functools_lru_cache import lru_cache

from werkzeug import secure_filename

from yumrepos import log


NEW = "new"
OBSOLETE = "obsolete"


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


def remove(fname):
    if os.path.exists(fname):
        os.remove(fname)


def mark_as_new(filename):
    unmark_as_obsolete(filename)
    touch(filename + "." + NEW)


def unmark_as_new(filename):
    remove(filename + "." + NEW)


def mark_as_obsolete(filename):
    unmark_as_new(filename)
    touch(filename + "." + OBSOLETE)


def unmark_as_obsolete(filename):
    try:
        remove(filename + "." + OBSOLETE)
    except OSError:
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
    def __init__(self, repos_folder, createrepo_bins=['createrepo_c', 'createrepo'], allowed_extensions=None):
        self.repos_folder = os.path.abspath(repos_folder)
        self.md_folder = os.path.join(self.repos_folder, ".metadata")
        self.createrepo_bin = None
        self.allowed_extensions = allowed_extensions if allowed_extensions else set(["rpm"])
        for createrepo_bin in createrepo_bins:
            if find_executable(createrepo_bin):
                self.createrepo_bin = createrepo_bin
                break

        for dirname in (self.repos_folder, self.md_folder):
            try:
                os.mkdir(dirname)
            except OSError as e:
                if e.errno != 17:
                    raise

        log.info("repo folder: %s" % self.repos_folder)
        log.info("md folder: %s" % self.md_folder)
        log.info("createrepo binary: %s" % self.createrepo_bin)

    # repo stuff

    def is_allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1] in self.allowed_extensions

    @staticmethod
    def is_allowed_reponame(reponame):
        if reponame.startswith("repodata"):
            return False
        if reponame.startswith("."):
            return False
        return True

    def create_rpm_metadata(self, filename):
        md_dir = os.path.join(self.md_folder, os.path.basename(filename))
        log.debug("md dir: %s" % md_dir)
        if os.path.exists(md_dir):
            return
        os.mkdir(md_dir)
        subprocess.check_call([
            self.createrepo_bin,
            "-n", filename,
            "-o", md_dir,
            "--update",
            os.path.dirname(filename)])

    def create_repo_metadata(self, reponame):
        log.debug("creating metadata for %s" % os.path.join(self.repos_folder, reponame))
        if not self.is_allowed_reponame(reponame):
            log.error("invalid")
            return
        if not self.createrepo_bin:
            touch(os.path.join(self.repos_folder, reponame, "repodata.faked"))
            return
        with open(os.devnull, "w") as fnull:
            for filename in os.listdir(os.path.join(self.repos_folder, reponame)):
                if filename.endswith("rpm"):
                    self.create_rpm_metadata(os.path.join(self.repos_folder, reponame, filename))
            subprocess.check_call([self.createrepo_bin,
                                   "--update",
                                   os.path.join(self.repos_folder, reponame)],
                                  stdout=fnull,
                                  stderr=fnull)

    def create_repo(self, reponame):
        try:
            log.debug("trying to create_repo %s" % self._to_path(reponame))
            os.mkdir(self._to_path(reponame))
        except OSError as e:
            if e.errno != 17:
                log.error(e)
                if e.errno == 2:
                    return ('', 404)
                raise
        log.info("repo %s created!" % reponame)
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
            mark_as_new(complete_filename)
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
        mark_as_obsolete(filename)
        return ('', 204)

    def is_link(self, reponame):
        return os.path.islink(self._to_path(reponame))

    @lru_cache()
    def get_rpm_info(self, reponame, rpmname):
        filename = self._to_path(reponame, rpmname)
        return subprocess.check_output(["rpm", "-qpi", filename])

    def list_repos(self):
        log.debug("listing %s" % self.repos_folder)
        return os.listdir(self.repos_folder)

    def list_rpms(self, reponame):
        log.debug("listing %s" % os.listdir(self._to_path(reponame)))
        return [file for file in os.listdir(self._to_path(reponame))
                if fnmatch(file, '*.rpm')]

    def get_filename(self, reponame, path=None):
        return self._to_path(reponame, path)

    def walk_repos(self):
        for dirpath, dirnames, filenames in os.walk(self.repos_folder):
            dirnames[:] = [d for d in dirnames if d != "repodata"]
            yield dirpath.replace(self.repos_folder, '')[1:]

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
                if action == OBSOLETE:
                    os.unlink(full_path)
                    unmark_as_obsolete(full_path)
                if action == NEW:
                    unmark_as_new(full_path)

    def split_action(self, full_filename):
        if full_filename.endswith(NEW) or full_filename.endswith(OBSOLETE):
            return full_filename.rsplit(".", 1)
        return (full_filename, None)
