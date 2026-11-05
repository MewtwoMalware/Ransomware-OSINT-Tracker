import json
import unittest
from unittest.mock import patch, MagicMock

from scripts import victim_tracker


class TestRansomLook(unittest.TestCase):

    @patch("scripts.victim_tracker.urllib.request.urlopen")
    def test_fetch_valid_posts(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "posts": [
                {
                    "group_name": "TestGroup",
                    "post_title": "Example Victim",
                    "discovered": "2026-11-05"
                }
            ]
        }).encode("utf-8")

        mock_urlopen.return_value.__enter__.return_value = mock_response

        posts = victim_tracker.fetch_ransomlook_posts()

        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["group_name"], "TestGroup")

    @patch("scripts.victim_tracker.urllib.request.urlopen")
    def test_invalid_json(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"not valid json"

        mock_urlopen.return_value.__enter__.return_value = mock_response

        with self.assertRaises(ValueError):
            victim_tracker.fetch_ransomlook_posts()

    @patch("scripts.victim_tracker.urllib.request.urlopen")
    def test_missing_posts_key(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "results": []
        }).encode("utf-8")

        mock_urlopen.return_value.__enter__.return_value = mock_response

        with self.assertRaises(ValueError):
            victim_tracker.fetch_ransomlook_posts()

    @patch("scripts.victim_tracker.urllib.request.urlopen")
    def test_posts_not_a_list(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "posts": {}
        }).encode("utf-8")

        mock_urlopen.return_value.__enter__.return_value = mock_response

        with self.assertRaises(ValueError):
            victim_tracker.fetch_ransomlook_posts()

    @patch("scripts.victim_tracker.urllib.request.urlopen")
    def test_invalid_post_entry(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "posts": ["invalid entry"]
        }).encode("utf-8")

        mock_urlopen.return_value.__enter__.return_value = mock_response

        with self.assertRaises(ValueError):
            victim_tracker.fetch_ransomlook_posts()

    @patch("scripts.victim_tracker.urllib.request.urlopen")
    def test_connection_error(self, mock_urlopen):
        mock_urlopen.side_effect = victim_tracker.urllib.error.URLError(
            "Connection failed"
        )

        with self.assertRaises(RuntimeError):
            victim_tracker.fetch_ransomlook_posts()

    @patch("scripts.victim_tracker.urllib.request.urlopen")
    def test_timeout(self, mock_urlopen):
        mock_urlopen.side_effect = TimeoutError()

        with self.assertRaises(TimeoutError):
            victim_tracker.fetch_ransomlook_posts()


if __name__ == "__main__":
    unittest.main()
