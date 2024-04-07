#!/usr/bin/env python3
"""
Tests the utils model
"""

import unittest
from parameterized import parameterized
from utils import *
from typing import Mapping, Sequence, Any

class TestAccessNestedMap(unittest.TestCase):
    """
    class to test the access_nested_map
    """
    @parameterized.expand([
        [{"a": 1}, ("a"), 1],
        [{"a": {"b": 2}}, ("a"), {"b": 2}],
        [{"a": {"b": 2}}, ("a", "b"), 2]
        ])
    def test_access_nested_map(self, nested_map: Mapping, path: Sequence, expected: Any):
        """tests the access_nested_map function."""
        self.assertEqual(access_nested_map(nested_map, path), expected)


if __name__ == '__main__':
    """
    Runs the test
    """
    unittest.main()
