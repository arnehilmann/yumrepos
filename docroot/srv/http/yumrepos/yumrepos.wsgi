from os.path import dirname, abspath, join

from yumrepos.app import create_application
from yumrepos.fs_backend import FsBackend

backend = FsBackend(join(dirname(abspath(__file__)), "repos"))
application = create_application(backend)
