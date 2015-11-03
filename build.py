from pybuilder.core import use_plugin, init, Author

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.integrationtest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")


name = "yum-repos"
summary = "yum-repos: simple yum repositories with minimal rest api"
url = "https://github.com/arnehilmann/yum-repos"
version = "0.1"

authors = [Author('Arne Hilmann', 'arne.hilmann@gmail.com')]

description = """yum-repos
- serve yum repositories as simple folders
- ... via web server
- offer rest api for
   - create/remove/link of repositories
   - upload/stage/remove of rpms
"""

default_task = ["clean", "analyze", "publish"]


@init
def set_properties(project):
    project.build_depends_on('requests')

    project.depends_on("flask")

    project.rpm_release = 0
    project.get_property('distutils_commands').append('bdist_rpm')
