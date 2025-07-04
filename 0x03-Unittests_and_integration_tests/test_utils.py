#!/usr/bin/env python3
"""
unit tests for access_nested_map
function
"""


import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize
from typing import Mapping, Sequence, Any
from client import GithubOrgClient


class TestAccessNestedMap(unittest.TestCase):
    """
    class to test neseted map function
    """

    @parameterized.expand(
        [
            ({"a": 1}, ("a",), 1),
            ({"a": {"b": 2}}, ("a",), {"b": 2}),
            ({"a": {"b": 2}}, ("a", "b"), 2),
        ]
    )
    def test_access_nested_map(
        self, nested_map: Mapping, path: Sequence, expected: Any
    ):
        """
        Tests the nested map function with different inputs
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand(
        [
            ({}, ("a",), "'a'"),
            ({"a": 1}, ("a", "b"), "'b'"),
        ]
    )
    def test_access_nested_map_exception(
        self, nested_map: Mapping, path: Sequence, expected: Any
    ):
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

    @parameterized.expand(
        [
            ("http://example.com", {"payload": True}),
            ("http://holberton.io", {"payload": False}),
        ]
    )
    @patch("utils.requests.get")
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


class TestMemoize(unittest.TestCase):
    """ "
    Test class for memoization functionality
    """

    def test_memoize(self):
        """
        memoization
        method
        """

        class TestClass:
            """
            test class
            """

            def a_method(self):
                """
                returns 42
                """
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        with patch.object(TestClass, "a_method",
                          return_value=42) as mock_method:
            mock_object = TestClass()
            result_1 = mock_object.a_property
            result_2 = mock_object.a_property

            self.assertEqual(result_1, 42)
            self.assertEqual(result_2, 42)
            mock_method.assert_called_once()


class TestGithubOrgClient(unittest.TestCase):
    """
    Testclass for github client
    """

    @parameterized.expand(
        [
            ["google",
                {"repos_url": "https://api.github.com/orgs/google/repos"}],
            ["abc", {"repos_url": "https://api.github.com/orgs/abc/repos"}],
        ]
    )
    @patch("client.get_json")
    def test_org(self, org_name: str, expected: dict,
                 mock_get_json: Mock) -> None:
        """
        testing th org propert
        """
        org_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.return_value = expected
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected)
        mock_get_json.assert_called_once_with(org_url)

    def test_public_repos_url(self) -> None:
        """
        tests _public_repos_url property
        """
        with patch.object(
            GithubOrgClient, "_public_repos_url", new_callable=PropertyMock
        ) as mock_method:
            ret_val = "https://api.github.com/orgs/test/repos"
            mock_method.return_value = ret_val
            obj = GithubOrgClient("test")
            self.assertEqual(
                obj._public_repos_url, "https://api.github.com/orgs/test/repos"
            )

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json: Mock) -> None:
        """
        unit test for public_repos method
        """
        test_payload = [{"name": "repo1"}, {"name": "repo2"}]
        with patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock
        ) as mock_url:
            url = "https://api.github.com/orgs/test/repos"
            mock_url.return_value = url
            mock_get_json.return_value = test_payload
            client = GithubOrgClient("test")
            self.assertEqual(client.public_repos(), ["repo1", "repo2"])
            mock_url.assert_called_once()
            mock_get_json.assert_called_once_with(url)


if __name__ == "__main__":
    """
    main function
    """
    unittest.main()
