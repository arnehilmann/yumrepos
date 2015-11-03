import os
from fnmatch import fnmatch
import json

from flask import Flask, request, abort, Blueprint, send_file

from fs_backend import FsBackend


app = Flask(__name__)
app.config['ALLOWED_EXTENSIONS'] = set(['rpm'])


def add_repos_routes(repos_dir):
    repos = Blueprint('repos', __name__)

    @repos.route('/', methods=['GET'])
    def get_repos():
        return json.dumps(os.listdir(repos_dir), indent=4)

    @repos.route('/<reponame>', methods=['GET'])
    def get_repo(reponame):
        return json.dumps([file for file in os.listdir(os.path.join(repos_dir, reponame))
                           if fnmatch(file, '*.rpm')], indent=4)

    @repos.route('/<reponame>/<rpmname>', methods=['GET'])
    def get_rpm_redirected(reponame, rpmname):
        filename = os.path.join(repos_dir, reponame, rpmname)
        return send_file(filename)

    @repos.route('/<reponame>/repodata/<filename>')
    def serve_repodata(reponame, filename):
        static_filename = os.path.join(repos_dir, reponame, 'repodata', filename)
        return send_file(static_filename)

    app.register_blueprint(repos, url_prefix='/repos')


def add_admin_routes(backend):
    admin = Blueprint('admin', __name__)

    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

    @admin.route('/ready')
    def is_ready():
        return ('', 200)

    @admin.route('/repos/<reponame>', methods=['PUT'])
    def create_repo(reponame):
        print "create_repo %s" % reponame
        if 'link_to' in request.args:
            link_to = request.args['link_to']
            if not backend.exists(link_to):
                return ('%s not a repo' % link_to, 404)
            return backend.create_repo_link(reponame, link_to)
        return backend.create_repo(reponame)

    @admin.route('/repos/<reponame>', methods=['DELETE', 'DELETERECURSIVLY'])
    def remove_repo(reponame):
        if backend.is_link(reponame):
            return backend.remove_repo_link(reponame)
        recursivly = request.method == 'DELETERECURSIVLY'
        return backend.remove_repo(reponame, recursivly)

    @admin.route('/repos/<reponame>', methods=['POST'])
    def upload_rpm(reponame):
        file = request.files['rpm']
        if file and allowed_file(file.filename):
            return backend.upload_rpm(reponame, file)

        return "%s not a valid rpm" % file.filename, 400

    @admin.route('/repos/<reponame>/<rpmname>/stageto/<targetreponame>', methods=['PUT', 'STAGE'])
    def stage_rpm(reponame, rpmname, targetreponame):
        if not backend.exists(reponame, rpmname):
            return "rpm '%s/%s' does not exist" % (reponame, rpmname), 404
        if not backend.exists(targetreponame):
            return "target repo '%s' does not exist" % targetreponame, 404
        if backend.exists(targetreponame, rpmname):
            abort(409)
        return backend.stage(reponame, rpmname, targetreponame)

    @admin.route('/repos/<reponame>/<rpmname>/info', methods=['GET'])
    def get_rpm_info(reponame, rpmname):
        return (str(backend.get_rpm_info(reponame, rpmname)), 200)

    @admin.route('/repos/<reponame>/<rpmname>', methods=['DELETE'])
    def remove_rpm(reponame, rpmname):
        return backend.remove_rpm(reponame, rpmname)

    @admin.route('/repos/<reponame>/is_link', methods=['GET'])
    def is_repo_a_link(reponame):
        if backend.is_link(reponame):
            return ('true', 200)
        return ('false', 200)

    @admin.route('/shutdown', methods=['POST'])
    def shutdown():
        request.environ.get('werkzeug.server.shutdown')()
        return ('Shutdown NOW', 200)

    app.register_blueprint(admin, url_prefix='/admin')


def configure(repos_dir):
    print "repos dir: %s" % repos_dir
    backend = FsBackend(repos_dir, 'createrepo_c')
    backend.init_env()

    add_repos_routes(repos_dir)
    add_admin_routes(backend)
