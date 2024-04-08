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

    def test_public_repos_url(self) -> None:
        """
        tests that list of repos is
        as expected from payload
        """
        mock_payload = {"repos_url":
                        "https://api.github.com/orgs/example/repos"}

        with patch.object(GithubOrgClient, 'org',
                          new=PropertyMock(return_value=mock_payload)):
            client: GithubOrgClient = GithubOrgClient("repos")

            result: str = client._public_repos_url
            expected_url: str = mock_payload["repos_url"]

            self.assertEqual(result, expected_url)

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: Mock) -> None:
        """
        tests list of repos is expected from payload
        """

        expected_url = "https://api.github.com/orgs/repos"
        payload = [{"name": "repo1"}, {"name": "repo2"}]
        mock_get_json.return_value = payload

        with patch.object(GithubOrgClient, '_public_repos_url',
                          new=PropertyMock(return_value=expected_url)):
            client = GithubOrgClient("example")

            repos = client.public_repos()

            mock_get_json.assert_called_once_with(expected_url)

            expected_repos = ["repo1", "repo2"]
            self.assertEqual(repos, expected_repos)


if __name__ == '__main__':
    """
    Runs the tests
    """
    unittest.main()
