#!/usr/bin/env python
from __future__ import print_function

import os
import logging
import select
import shutil
import subprocess
import sys
import threading
import time
import unittest

from yumrepos.app import create_application
from yumrepos.fs_backend import FsBackend


def call(popenargs, logger, stdout_log_level=logging.INFO, stderr_log_level=logging.ERROR, **kwargs):
    """
    Variant of subprocess.call that accepts a logger instead of stdout/stderr,
    and logs stdout messages via logger.debug and stderr messages via
    logger.error.
    """
    child = subprocess.Popen(popenargs, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, **kwargs)

    log_level = {child.stdout: stdout_log_level,
                 child.stderr: stderr_log_level}

    def check_io():
        ready_to_read = select.select([child.stdout, child.stderr], [], [], 1000)[0]
        for io in ready_to_read:
            line = io.readline()
            logger.log(log_level[io], line[:-1])

    # keep checking stdout/stderr until the child exits
    while child.poll() is None:
        check_io()

    check_io()  # check again to catch anything after the process exits

    return child.wait()


class Test(unittest.TestCase):

    def test_full_lifecycle(self):
        self._run_test("../bash/full-lifecycle-tests")

    def test_nested_repos(self):
        self._run_test("../bash/nested-repos-tests")

    def test_bulk_repos(self):
        self._run_test("../bash/bulk-repos-tests")

    def _run_test(self, script, port=28080):
        host = "http://localhost:%i" % port
        repo_dir = os.path.join(os.getcwd(), "target", "integrationtests-%i" % port)

        def testrunner():
            application = create_application(FsBackend(os.path.join(repo_dir, "repos")))
            application.run("0.0.0.0", port)

        t = threading.Thread(target=testrunner)
        t.setDaemon(True)
        t.start()

        time.sleep(1)

        logger = logging.getLogger("testclient")
        result = call(" ".join([os.path.join(os.path.dirname(__file__), script),
                                host,
                                "file://%s" % repo_dir]),
                      logger,
                      shell=True)

        t.join(2)
        print("server still alive? %s" % t.is_alive())
        self.assertEqual(result, 0)

        shutil.rmtree(repo_dir)


if __name__ == "__main__":
    sys.exit(unittest.main())
