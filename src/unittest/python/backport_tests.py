#!/usr/bin/env python
from __future__ import print_function

import sys

try:
    from functools import lru_cache
    sys.exit(0)
except ImportError:
    pass

import unittest

from backports import functools_lru_cache


class Test(unittest.TestCase):
    def test_with_bound_cache(self):
        @functools_lru_cache.lru_cache()
        def cachy(*args):
            return True
        self.assertTrue(cachy("foo"))
        self.assertTrue(cachy("bar"))
        self.assertTrue(cachy("foo"))
        print(cachy.cache_info())
        cachy.cache_clear()

    def test_without_cache(self):
        @functools_lru_cache.lru_cache(maxsize=None)
        def cachy(*args):
            return True
        self.assertTrue(cachy("foo"))
        self.assertTrue(cachy("bar"))
        self.assertTrue(cachy("foo"))
        print(cachy.cache_info())
        cachy.cache_clear()

    def test_with_boundless_cache(self):
        @functools_lru_cache.lru_cache(maxsize=0)
        def cachy(*args):
            return True
        self.assertTrue(cachy("foo"))
        self.assertTrue(cachy("bar"))
        self.assertTrue(cachy("foo"))
        print(cachy.cache_info())
        cachy.cache_clear()


if __name__ == "__main__":
    sys.exit(unittest.main())
