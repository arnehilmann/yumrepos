import fnmatch
import json
import os

from flask import Flask, request, abort, send_file, redirect

from fs_backend import FsBackend


app = Flask(__name__)
app.debug = False

app.config['ALLOWED_EXTENSIONS'] = set(['rpm'])
app.config['SERVE_STATIC_FILES'] = False

REPOS_FOLDER = os.path.abspath('/srv/http/repos')
app.config['BACKEND'] = FsBackend(REPOS_FOLDER, 'createrepo_c')


@app.before_first_request
def init_env():
    app.config['BACKEND'].init_env()


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/repos/<reponame>', methods=['PUT'])
def create_repo(reponame):
    if 'link_to' in request.args:
        link_to = request.args['link_to']
        if not app.config['BACKEND'].exists(link_to):
            return ('%s not a repo' % link_to, 404)
        return app.config['BACKEND'].create_repo_link(reponame, link_to)
    return app.config['BACKEND'].create_repo(reponame)


@app.route('/repos/<reponame>', methods=['DELETE', 'DELETERECURSIVLY'])
def remove_repo(reponame):
    backend = app.config['BACKEND']
    if backend.is_link(reponame):
        return app.config['BACKEND'].remove_repo_link(reponame)
    recursivly = request.method == 'DELETERECURSIVLY'
    return app.config['BACKEND'].remove_repo(reponame, recursivly)


@app.route('/repos/<reponame>', methods=['POST'])
def upload_rpm(reponame):
    file = request.files['rpm']
    if file and allowed_file(file.filename):
        return app.config['BACKEND'].upload_rpm(reponame, file)

    return "%s not a valid rpm" % file.filename, 400


@app.route('/repos/<reponame>/<rpmname>/stageto/<targetreponame>', methods=['PUT', 'STAGE'])
def stage_rpm(reponame, rpmname, targetreponame):
    backend = app.config['BACKEND']
    if not backend.exists(reponame, rpmname):
        return "rpm '%s/%s' does not exist" % (reponame, rpmname), 404
    if not backend.exists(targetreponame):
        return "target repo '%s' does not exist" % targetreponame, 404
    if backend.exists(targetreponame, rpmname):
        abort(409)
    return backend.stage(reponame, rpmname, targetreponame)


@app.route('/repos/<reponame>/<rpmname>', methods=['DELETE'])
def remove_rpm(reponame, rpmname):
    return app.config['BACKEND'].remove_rpm(reponame, rpmname)


@app.route('/repos/<reponame>/is_link', methods=['GET'])
def is_repo_a_link(reponame):
    if app.config['BACKEND'].is_link(reponame):
        return ('true', 200)
    return ('false', 200)


@app.route('/repos/<reponame>', methods=['GET'])
def get_repo_info(reponame):
    if 'is_link' in request.args:
        if app.config['BACKEND'].is_link(reponame):
            return ('true', 200)
        return ('false', 200)
    abort(400)


if app.config['SERVE_STATIC_FILES']:
    @app.route('/', methods=['GET'])
    def get_repos():
        return json.dumps(os.listdir(REPOS_FOLDER), indent=4)

    @app.route('/<reponame>', methods=['GET'])
    def get_repo(reponame):
        return json.dumps([file for file in os.listdir(os.path.join(REPOS_FOLDER, reponame))
                           if fnmatch.fnmatch(file, '*.rpm')], indent=4)

    @app.route('/strange/url/repos/<reponame>/<rpmname>', methods=['GET'])
    def get_rpm(reponame, rpmname):
        filename = os.path.join(REPOS_FOLDER, reponame, rpmname)
        return send_file(filename)

    @app.route('/<reponame>/<rpmname>', methods=['GET'])
    def get_rpm_redirected(reponame, rpmname):
        return redirect('/strange/url/repos/%s/%s' % (reponame, rpmname))

    @app.route('/<reponame>/repodata/<filename>')
    def serve_repodata(reponame, filename):
        static_filename = os.path.join(REPOS_FOLDER, reponame, 'repodata', filename)
        return send_file(static_filename)
