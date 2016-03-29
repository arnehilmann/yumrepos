import sys
from pybuilder.core import use_plugin, init, Author

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.integrationtest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin('copy_resources')
use_plugin('filter_resources')

name = "yum-repos"
summary = "yum-repos: simple yum repositories with minimal rest api"
url = "https://github.com/arnehilmann/yum-repos"
version = "0.7.5"

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

    project.rpm_release = "py%i%i" % sys.version_info[0:2]
    project.python_version_range = "python >= {0}.{1}, python <= {0}.{1}.9999".format(*sys.version_info[0:2])

    project.set_property('copy_resources_target', '$dir_dist')
    project.get_property('copy_resources_glob').extend(['setup.cfg'])
    project.get_property('filter_resources_glob').extend(['**/setup.cfg'])
