import unittest
from core.matcher import (
    is_duration_acceptable,
    is_blacklisted,
    is_channel_whitelisted,
    score_candidate,
    get_active_whitelist
)


class TestSmartOfficialMatcher(unittest.TestCase):
    def test_is_duration_acceptable_within_tolerance(self):
        # ±3 seconds tolerance
        self.assertTrue(is_duration_acceptable(180, 180, tolerance=3))
        self.assertTrue(is_duration_acceptable(180, 182, tolerance=3))
        self.assertTrue(is_duration_acceptable(180, 177, tolerance=3))
        self.assertFalse(is_duration_acceptable(180, 185, tolerance=3))
        self.assertFalse(is_duration_acceptable(180, 170, tolerance=3))

    def test_is_duration_acceptable_unknown_fallback(self):
        # If target or candidate duration is <= 0, should not disqualify
        self.assertTrue(is_duration_acceptable(0, 180, tolerance=3))
        self.assertTrue(is_duration_acceptable(180, 0, tolerance=3))

    def test_is_blacklisted_detects_junk(self):
        self.assertTrue(is_blacklisted("Artist - Song (Slowed + Reverb)", "Channel"))
        self.assertTrue(is_blacklisted("Artist - Song Live at Istanbul", "Channel"))
        self.assertTrue(is_blacklisted("Artist - Song (Cover by Fan)", "Channel"))
        self.assertFalse(is_blacklisted("Artist - Song (Official Audio)", "Artist - Topic"))

    def test_score_candidate_penalizes_junk(self):
        spotify_info = {"title": "Seni Dert Etmeler", "duration": 180}
        candidate_clean = {
            "title": "Madrigal - Seni Dert Etmeler (Official Audio)",
            "channel": "Madrigal - Topic",
            "duration": 180
        }
        candidate_junk = {
            "title": "Madrigal Seni Dert Etmeler Live Slowed Reverb Cover",
            "channel": "FanChannel123",
            "duration": 180
        }
        score_clean = score_candidate(spotify_info, candidate_clean)
        score_junk = score_candidate(spotify_info, candidate_junk)
        self.assertGreater(score_clean, 100.0)
        self.assertEqual(score_junk, 0.0)

    def test_duration_boundary_conditions(self):
        self.assertTrue(is_duration_acceptable(100.0, 103.0, tolerance=3.0))
        self.assertTrue(is_duration_acceptable(100.0, 97.0, tolerance=3.0))
        self.assertFalse(is_duration_acceptable(100.0, 103.1, tolerance=3.0))
        self.assertFalse(is_duration_acceptable(100.0, 96.9, tolerance=3.0))

    def test_remix_filtering_when_original_is_not_remix(self):
        # Candidate has "remix", but original does not -> blacklist
        self.assertTrue(is_blacklisted("Track Name (Club Remix)", "Uploader", original_title="Track Name"))
        # Candidate has "remix", and original also has "remix" -> allowed
        self.assertFalse(is_blacklisted("Track Name (Club Remix)", "Uploader", original_title="Track Name (Club Remix)"))

    def test_channel_whitelisting(self):
        self.assertTrue(is_channel_whitelisted("Daft Punk - Topic"))
        self.assertTrue(is_channel_whitelisted("Netd Müzik"))
        self.assertTrue(is_channel_whitelisted("Sony Music Turkey"))
        self.assertFalse(is_channel_whitelisted("RandomFan99"))

    def test_duration_zero_requires_official_authority(self):
        spotify_info = {"artist": "Madrigal", "title": "Seni Dert Etmeler", "duration": 0}
        cand_topic = {
            "title": "Seni Dert Etmeler",
            "channel": "Madrigal - Topic",
            "duration": 0
        }
        cand_fan = {
            "title": "Seni Dert Etmeler",
            "channel": "RandomBootlegUploader",
            "duration": 0
        }
        score_official = score_candidate(spotify_info, cand_topic)
        score_fan = score_candidate(spotify_info, cand_fan)
        self.assertGreater(score_official, 70.0)
        self.assertLess(score_fan, 70.0)


if __name__ == "__main__":
    unittest.main()
