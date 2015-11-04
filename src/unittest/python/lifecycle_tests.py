#!/usr/bin/env python

import unittest
from yumrepos import app as application
from yumrepos import app_configure, FsBackend
import requests
import subprocess
import os
import sys
import threading


class Test(unittest.TestCase):

    PORT = 8080
    HOST = "http://localhost:%i" % PORT

    def test(self):
        def testrunner():
            app_configure(FsBackend('/tmp'), serve_static=True)
            application.run("0.0.0.0", self.PORT)

        t = threading.Thread(target=testrunner)
        t.setDaemon(True)
        t.start()

        result = subprocess.call(" ".join([os.path.join(os.path.dirname(__file__),
                                                        "../resources/full-lifecycle-tests"), self.HOST]), shell=True)

        requests.post("%s/admin/shutdown" % self.HOST)
        t.join(4)
        print "server still alive? %s" % t.is_alive()
        self.assertEqual(result, 0)


if __name__ == "__main__":
    sys.exit(unittest.main())
