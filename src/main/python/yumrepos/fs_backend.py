import glob
import os
import shutil
import subprocess

from werkzeug import secure_filename


class FsBackend(object):
    def __init__(self, repos_folder, createrepo_bin):
        self.repos_folder = repos_folder
        self.createrepo_bin = createrepo_bin

    def init_env(self):
        try:
            os.mkdir(self.repos_folder)
        except OSError as e:
            if e.errno != 17:
                raise

    def create_repo_metadata(self, reponame):
        subprocess.check_call([self.createrepo_bin, os.path.join(self.repos_folder, reponame)])

    def create_repo(self, reponame):
        try:
            os.mkdir(self._to_path(reponame))
        except OSError as e:
            if e.errno != 17:
                raise
        self.create_repo_metadata(reponame)
        return ('', 201)

    def remove_repo(self, reponame):
        repopath = self._to_path(reponame)
        if not os.path.exists(repopath):
            return ('', 404)
        if len(glob.glob(os.path.join(repopath, "*.rpm"))) > 0:
            return "repo not empty, aborting", 409
        try:
            shutil.rmtree(repopath)
        except OSError as e:
            if e.errno == 39:
                return ('', 409)
            raise
        return ('', 204)

    def upload_rpm(self, reponame, file):
        filename = secure_filename(file.filename)
        complete_filename = self._to_path(reponame, filename)
        if os.path.exists(complete_filename):
            return "%s already exists" % filename, 409
        try:
            file.save(complete_filename)
            self.create_repo_metadata(reponame)
            return ('', 201)
        except IOError as e:
            if e.errno == 2:
                return ('', 404)

    def _to_path(self, reponame, rpmname=''):
        return os.path.join(self.repos_folder, reponame, rpmname)

    def exists(self, reponame, rpmname=''):
        return os.path.exists(self._to_path(reponame, rpmname))

    def stage(self, source, rpm, target):
        shutil.move(self._to_path(source, rpm), self._to_path(target, rpm))
        self.create_repo_metadata(source)
        self.create_repo_metadata(target)
        return '', 201

    def remove_rpm(self, reponame, rpmname):
        filename = self._to_path(reponame, rpmname)
        try:
            os.unlink(filename)
            self.create_repo_metadata(reponame)
        except OSError as e:
            if e.errno == 2:
                return ('', 404)
            raise
        return ('', 204)
