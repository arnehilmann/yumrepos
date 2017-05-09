from __future__ import print_function
import json
import os

from braceexpand import braceexpand
from flask import Flask, request, Blueprint, send_file  # , abort

from yumrepos import log


def add_repos_routes(app, backend):
    repos = Blueprint('repos', __name__)

    @repos.route('/', defaults={'path': ''})
    @repos.route('/<path:path>', methods=['GET'])
    def get_content(path):
        if backend.isfile(path):
            return send_file(backend.get_filename(path))
        if backend.exists(path):
            return (json.dumps(backend.list_rpms(path)), 200)
        return ('', 404)

    app.register_blueprint(repos, url_prefix='/repos')


def add_admin_routes(app, backend):
    admin = Blueprint('admin', __name__)

    @admin.route('/ready')
    def is_ready():
        log.info("/ready called (log)")
        return ('', 204)

    @admin.route('/update')
    @admin.route('/update-all-metadata')
    def update_all_metadata():
        backend.update_all_metadata()
        return ('', 204)

    @admin.route('/repos/<path:reponame>', methods=['PUT'])
    def create_repo(reponame):
        if not backend.is_allowed_reponame(reponame):
            return ('%s not an allowed reponame' % reponame, 403)
        log.info("create_repo %s" % reponame)
        if 'link_to' in request.args:
            link_to = request.args['link_to']
            if not backend.exists(link_to):
                return ('%s not a repo' % link_to, 404)
            return backend.create_repo_link(reponame, link_to)
        return backend.create_repo(reponame)

    @admin.route('/repos', methods=['POST'])
    def create_bulk_repos():
        spec = request.form.get('pathspec')
        if not spec:
            return ('no pathspec parameter given?!', 400)
        log.info("pathspec: %s" % spec)
        reponames = list(braceexpand(spec))
        log.info("expanded pathes: %s" % ", ".join(reponames))
        for reponame in reponames:
            if not backend.is_allowed_reponame(reponame):
                return ('%s not an allowed reponame' % reponame, 403)
        for reponame in reponames:
            text, status = backend.create_repo(reponame)
            if status != 201:
                return (text, status)
        return ('', 201)

    @admin.route('/repos/<path:reponame>', methods=['DELETE', 'DELETERECURSIVLY'])
    def remove_repo(reponame):
        if backend.is_link(reponame):
            return backend.remove_repo_link(reponame)
        recursivly = request.method == 'DELETERECURSIVLY'
        return backend.remove_repo(reponame, recursivly)

    @admin.route('/repos/<path:reponame>', methods=['GET'])
    def get_repo(reponame):
        args = request.args
        if "update" in args or "update-metadata" in args:
            try:
                return backend.create_repo_metadata(reponame)
            except Exception:
                return ('', 404)
        if "is_link" in args:
            if backend.is_link(reponame):
                return ('true', 200)
            return ('false', 200)
        return ('', 403)

    @admin.route('/repos/<path:reponame>', methods=['POST'])
    def upload_rpm(reponame):
        rpm_file = request.files['rpm']
        if rpm_file and backend.is_allowed_file(rpm_file.filename):
            return backend.upload_rpm(reponame, rpm_file)

        return "%s not a valid rpm" % rpm_file.filename, 400

    def _precheck_stage_or_copy(reponame, rpmname, targetreponame):
        if not targetreponame:
            return ("no stageto or copyto parameter given?!", 400)
        if not backend.exists(reponame, rpmname):
            return ("rpm '%s/%s' does not exist" % (reponame, rpmname), 404)
        log.info("target repo name: %s" % targetreponame)
        if not backend.exists(targetreponame):
            return ("target repo '%s' does not exist" % targetreponame, 404)
        if backend.exists(targetreponame, rpmname):
            return ("", 409)
        return None  # no problems found

    @admin.route('/repos/<path:reponame>/<rpmname>.rpm', methods=['STAGE'])
    def stage_rpm(reponame, rpmname):
        rpmname = rpmname + ".rpm"
        targetreponame = request.args.get("stageto")
        problem = _precheck_stage_or_copy(reponame, rpmname, targetreponame)
        return problem if problem else backend.stage(reponame, rpmname, targetreponame)

    @admin.route('/repos/<path:reponame>/<rpmname>.rpm', methods=['COPY'])
    def copy_rpm(reponame, rpmname):
        rpmname = rpmname + ".rpm"
        targetreponame = request.args.get("copyto")
        problem = _precheck_stage_or_copy(reponame, rpmname, targetreponame)
        return problem if problem else backend.copy(reponame, rpmname, targetreponame)

    @admin.route('/repos/<path:reponame>/<rpmname>.rpm', methods=['GET'])
    def get_rpm_info(reponame, rpmname):
        rpmname = rpmname + ".rpm"
        args = request.args
        if "info" in args:
            return backend.get_rpm_info(reponame, rpmname)
        if "stat" in args:
            attr = args.get("stat", None)
            try:
                return (str(backend.get_rpm_stat(reponame, rpmname, attr)), 200)
            except Exception:
                return ('', 404)
        return ('', 403)

    @admin.route('/repos/<path:reponame>/<rpmname>.rpm', methods=['DELETE'])
    def remove_rpm(reponame, rpmname):
        rpmname = rpmname + ".rpm"
        return backend.remove_rpm(reponame, rpmname)

    @admin.route('/shutdown', methods=['POST'])
    def shutdown():
        func = request.environ.get('werkzeug.server.shutdown')
        if func:
            func()
            return ('Shutdown NOW', 200)
        return ('Not in Standalone mode: Shutdown FORBIDDEN', 403)

    @admin.route('/rpms/<rpmname>.rpm', methods=['GET'])
    def get_direct_rpm(rpmname):
        # TODO extract get_rpm_* functions, here and under get_rpm_info
        rpmname = rpmname + ".rpm"
        args = request.args
        if "info" in args:
            return backend.get_rpm_info(os.path.join(".metadata", rpmname), rpmname)
        if "stat" in args:
            attr = args.get("stat", None)
            try:
                return (str(backend.get_rpm_stat(".metadata", rpmname, attr)), 200)
            except Exception:
                return ('', 404)
        return ('', 403)

    app.register_blueprint(admin, url_prefix='/admin/v1')


def create_application(backend):
    app = Flask(__name__)

    add_repos_routes(app, backend)
    add_admin_routes(app, backend)

    return app
