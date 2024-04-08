#!/usr/bin/env python3
"""
Tests the utils model
"""

import unittest
from unittest.mock import patch, Mock
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
    def test_access_nested_map(self, nested_map: Mapping, path:
                               Sequence, expected: Any):
        """tests the access_nested_map function."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        [{}, ("a"), "KeyError: 'a'"],
        [{"a": 1}, ("a", "b"), "KeyError: 'b'"]
        ])
    def test_access_nested_map_exception(self, nested_map: Mapping, path:
                                         Sequence, expected: Any):
        """
        tests if access _nested_map functon raises key error on missing key
        """
        self.assertRaises(KeyError, access_nested_map, nested_map, path)


class TestGetJson(unittest.TestCase):
    """
    Testcase for the getjson function
    """

    @parameterized.expand([
        ["http://example.com", {"payload": True}],
        ["http://holberton.io", {"payload": False}]
        ])
    @patch('utils.requests.get')
    def test_get_json(self, test_url: str, test_payload: dict,
                      mock_get: Mock):
        """
        tests for the test payload return
        """
        # set up mock response
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response

        # Call the get_json function
        result = get_json(test_url)

        # assert that the mocked get method was called once with the test_url
        mock_get.assert_called_once_with(test_url)

        # assert output is equal to test payload
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """
    Testcase for the memoize function in utils
    """
    def test_memoize(self):
        """
        tests the memoize decorator
        """

        class TestClass:
            """
            The test class
            """
            def a_method(self):
                """
                a method
                """
                return 42

            @memoize
            def a_property(self):
                """
                test property
                """
                return self.a_method()

        with patch.object(TestClass, 'a_method') as mock_a_method:
            # create test class instance
            test_instance = TestClass()

            # call property twice
            result1 = test_instance.a_property
            result2 = test_instance.a_property

            # assert method was called once
            mock_a_method.assert_called_once()


if __name__ == '__main__':
    """
    Runs the test
    """
    unittest.main()
