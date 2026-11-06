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

    def test_convert_ransomlook_post(self):
        post = {
            "group_name": "TestGroup",
            "post_title": "Example Victim",
            "discovered": "2026-11-05"
        }

        record = victim_tracker.convert_ransomlook_post(post)

        self.assertIsNotNone(record)
        self.assertEqual(record["group"], "TestGroup")
        self.assertEqual(record["victim"], "Example Victim")
        self.assertEqual(record["status"], "claimed")
        self.assertEqual(record["confidence"], "unverified")
        self.assertEqual(record["source"], "RansomLook")

    def test_convert_invalid_post(self):
        post = {
            "group_name": "",
            "post_title": "Example Victim"
        }

        record = victim_tracker.convert_ransomlook_post(post)

        self.assertIsNone(record)

    def test_import_skips_duplicates(self):
        post = {
            "group_name": "TestGroup",
            "post_title": "Example Victim",
            "discovered": "2026-11-05"
        }

        existing_record = victim_tracker.convert_ransomlook_post(post)

        imported = victim_tracker.import_ransomlook_posts(
            [post],
            [existing_record]
        )

        self.assertEqual(imported, [])

    def test_import_new_victim(self):
        post = {
            "group_name": "TestGroup",
            "post_title": "New Victim",
            "discovered": "2026-11-05"
        }

        imported = victim_tracker.import_ransomlook_posts(
            [post],
            []
        )

        self.assertEqual(len(imported), 1)
        self.assertEqual(imported[0]["victim"], "New Victim")

    @patch("scripts.victim_tracker.urllib.request.urlopen")
    def test_fetch_historical_valid_posts(self, mock_urlopen):
        response = MagicMock()
        response.read.return_value = json.dumps([
            {
                "group": "TestGroup",
                "post_title": "Test Victim",
                "discovered": "2026-01-15"
            }
        ]).encode("utf-8")

        mock_urlopen.return_value.__enter__.return_value = response

        posts = victim_tracker.fetch_ransomlook_historical_posts(
            "2026-01-01",
            "2026-02-01"
        )

        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["group"], "TestGroup")

        requested_url = mock_urlopen.call_args[0][0].full_url
        self.assertIn("2026-01-01", requested_url)
        self.assertIn("2026-02-01", requested_url)

    @patch("scripts.victim_tracker.urllib.request.urlopen")
    def test_fetch_historical_invalid_json(self, mock_urlopen):
        response = MagicMock()
        response.read.return_value = b"not valid json"

        mock_urlopen.return_value.__enter__.return_value = response

        with self.assertRaises(ValueError):
            victim_tracker.fetch_ransomlook_historical_posts(
                "2026-01-01",
                "2026-02-01"
            )

    @patch("scripts.victim_tracker.urllib.request.urlopen")
    def test_fetch_historical_response_not_list(self, mock_urlopen):
        response = MagicMock()
        response.read.return_value = json.dumps({
            "posts": []
        }).encode("utf-8")

        mock_urlopen.return_value.__enter__.return_value = response

        with self.assertRaises(ValueError):
            victim_tracker.fetch_ransomlook_historical_posts(
                "2026-01-01",
                "2026-02-01"
            )

    @patch("scripts.victim_tracker.urllib.request.urlopen")
    def test_fetch_historical_invalid_post_entry(self, mock_urlopen):
        response = MagicMock()
        response.read.return_value = json.dumps([
            "not a post"
        ]).encode("utf-8")

        mock_urlopen.return_value.__enter__.return_value = response

        with self.assertRaises(ValueError):
            victim_tracker.fetch_ransomlook_historical_posts(
                "2026-01-01",
                "2026-02-01"
            )

    def test_convert_historical_post(self):
        post = {
            "group_name": "TestGroup",
            "post_title": "Historical Victim",
            "discovered": "2026-01-15"
        }

        record = victim_tracker.convert_ransomlook_historical_post(post)

        self.assertIsNotNone(record)
        self.assertEqual(record["date"], "2026-01-15")
        self.assertEqual(record["status"], "claimed")
        self.assertEqual(record["confidence"], "unverified")
        self.assertEqual(record["source"], "RansomLook")

    def test_convert_historical_post_missing_date(self):
        post = {
            "group_name": "TestGroup",
            "post_title": "Victim Without Date"
        }

        record = victim_tracker.convert_ransomlook_historical_post(post)

        self.assertIsNone(record)

    def test_convert_historical_post_invalid_data(self):
        post = {
            "group_name": "",
            "post_title": "Invalid Victim",
            "discovered": "2026-01-15"
        }

        record = victim_tracker.convert_ransomlook_historical_post(post)

        self.assertIsNone(record)

if __name__ == "__main__":
    unittest.main()
