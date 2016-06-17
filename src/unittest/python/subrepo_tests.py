#!/usr/bin/env python
from __future__ import print_function

import os
import requests
import subprocess
import sys
import threading
import time
import unittest

from yumrepos.app import create_application
from yumrepos.fs_backend import FsBackend


class Test(unittest.TestCase):

    PORT = 28080
    HOST = "http://localhost:%i" % PORT

    def test(self):
        def testrunner():
            application = Server(FsBackend('/tmp'))
            application.run("0.0.0.0", self.PORT)

        t = threading.Thread(target=testrunner)
        t.setDaemon(True)
        t.start()

        time.sleep(1)

        result = subprocess.call(" ".join([os.path.join(os.path.dirname(__file__),
                                                        "../resources/subrepo-tests"), self.HOST]), shell=True)

        t.join(4)
        print("server still alive? %s" % t.is_alive())
        self.assertEqual(result, 0)


if __name__ == "__main__":
    sys.exit(unittest.main())
