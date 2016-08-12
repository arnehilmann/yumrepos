#!/usr/bin/env python
from __future__ import print_function

import sys
import unittest

import yumrepos.fs_backend as backend


class Test(unittest.TestCase):
    def test_check_output(self):
        result = backend.check_output_backported(["echo", "foo"])
        self.assertEqual(result, b"foo\n")


if __name__ == "__main__":
    sys.exit(unittest.main())
