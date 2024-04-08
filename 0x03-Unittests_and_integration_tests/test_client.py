#!/usr/bin/env python3
"""
Test module for client.GithuborgClient
"""
import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """
    Testcase for githuborgclient
    """
    @parameterized.expand([
        ["google",],
        ["abc",]
        ])
    @patch('client.get_json')
    def test_org(self, name: str, mock_get: Mock):
        """
        test for the org
        """
        client = GithubOrgClient(name)
        mock_response = Mock()
        mock_response.return_value = {"name": name}

        mock_get.return_value = mock_response

        result = client.org()

        org_url = f"https://api.github.com/orgs/{name}"
        mock_get.assert_called_once_with(org_url)

        self.assertEqual(result, {"name": name})

    def test_public_repos(self):
        """
        tests that list of repos is as expected from
        payload
        """
        mock_payload = {"repos_url":
                        "https://api.github.com/orgs/example/repos"}

        with patch.object(GithubOrgClient, 'org',
                          new=PropertyMock(return_value=mock_payload)):
            client = GithubOrgClient("example")

            result = client._public_repos_url
            expected_url = mock_payload["repos_url"]

            self.assertEqual(result, expected_url)


if __name__ == '__main__':
    """
    Runs the tests
    """
    unittest.main()
