#!/usr/bin/env python3
"""
unit tests for access_nested_map
function
"""


import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from utils import access_nested_map, get_json
from typing import Mapping, Sequence, Any


class TestAccessNestedMap(unittest.TestCase):
    """
    class to test neseted map function
    """
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
     ])
    def test_access_nested_map(self, nested_map: Mapping, path:
                               Sequence, expected: Any):
        """
        Tests the nested map function with different inputs
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "'a'"),
        ({"a": 1}, ("a", "b"), "'b'"),
    ])
    def test_access_nested_map_exception(self, nested_map: Mapping, path:
                                         Sequence, expected: Any):
        """
        tests if accessnestedmap function raises correct key errors
        """
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(str(context.exception), expected)


class TestGetJson(unittest.TestCase):
    """
    Test class for get_json function
    """

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False})
    ])
    @patch('utils.requests.get')
    def test_get_json(self, test_url: str, test_payload: dict, mock_get: Mock):
        """
        Tests the get_json function with mock data
        """
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response

        result = get_json(test_url)

        mock_get.assert_called_once_with(test_url)
        self.assertEqual(result, test_payload)


if __name__ == "__main__":
    """
    main function
    """
    unittest.main()
