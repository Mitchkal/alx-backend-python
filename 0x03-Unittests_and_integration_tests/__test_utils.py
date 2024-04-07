#!/usr/bin/env python3
"""
Tests the utils model
"""

import unittest
from utils import *


class TestAccessNestedMap(unittest.TestCase):
    """
    class to test the access_nested_map
    """
    @parametized.expand
    def test_access_nested_map(self):
        """tests the nested map method
        """
        nested_map = {"a": 1}, path = ("a",)
        self.assertEqual(access_nested_map(nested_map, path), 1)

        nested_map = {"a": {"b": 2}}, path = ("a",)
        self.assertEqual(access_nested_map(nested_map, path), {'b': 2})

        nested_map = {"a": {"b": 2}}, path = ("a", "b")
        self.assertEqual(access_nested_map(nested_map, path), 2)


if __name__ == '__main__':
    """
    Runs the test
    """
    unittest.main()
