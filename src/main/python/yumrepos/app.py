import json

from flask import Flask, request, abort, Blueprint, send_file


app = Flask(__name__)
app.config['ALLOWED_EXTENSIONS'] = set(['rpm'])


def add_repos_routes(backend):
    repos = Blueprint('repos', __name__)

    @repos.route('/', methods=['GET'])
    def list_repos():
        return json.dumps(backend.list_repos(), indent=4)

    @repos.route('/<reponame>', methods=['GET'])
    def list_rpms(reponame):
        return json.dumps(backend.list_rpms(reponame), indent=4)

    @repos.route('/<reponame>/<path:path>', methods=['GET'])
    def get_filename(reponame, path):
        return send_file(backend.get_filename(reponame, path))

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


def configure(backend, serve_static=False):
    add_admin_routes(backend)
    if serve_static:
        add_repos_routes(backend)
