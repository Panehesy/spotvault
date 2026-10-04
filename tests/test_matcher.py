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

    def test_channel_whitelisting_word_boundary_avoids_false_positives(self):
        self.assertFalse(is_channel_whitelisted("admc_gamer"))
        self.assertFalse(is_channel_whitelisted("subkmatrix"))
        self.assertFalse(is_channel_whitelisted("1234adventure"))
        self.assertFalse(is_channel_whitelisted("vevox_gamer"))
        self.assertTrue(is_channel_whitelisted("DMC Müzik"))
        self.assertTrue(is_channel_whitelisted("BKM"))
        self.assertTrue(is_channel_whitelisted("TaylorSwiftVEVO"))
        self.assertTrue(is_channel_whitelisted("4AD"))

    def test_whitelist_caching(self):
        from core.matcher import load_custom_labels
        import tempfile
        from pathlib import Path
        with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8", suffix=".txt") as tmp:
            tmp.write("custom_label_one\ncustom_label_two\n")
            tmp_path = Path(tmp.name)

        try:
            labels1 = load_custom_labels(tmp_path)
            labels2 = load_custom_labels(tmp_path)
            self.assertEqual(labels1, labels2)
            self.assertIn("custom_label_one", labels1)
            self.assertIn("custom_label_two", labels1)
        finally:
            tmp_path.unlink(missing_ok=True)

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
        self.assertEqual(score_fan, 0.0)

    def test_find_best_official_candidate_confidence_threshold(self):
        from core.matcher import find_best_official_candidate, MIN_OFFICIAL_CONFIDENCE
        self.assertEqual(MIN_OFFICIAL_CONFIDENCE, 70.0)

    def test_turkish_lower_normalization(self):
        from core.matcher import turkish_lower, normalize_for_matching
        self.assertEqual(turkish_lower("KADIKÖY"), "kadikoy")
        self.assertEqual(turkish_lower("kadıköy"), "kadikoy")
        self.assertEqual(turkish_lower("İSTANBUL"), "istanbul")
        self.assertEqual(turkish_lower("istanbul"), "istanbul")
        self.assertEqual(turkish_lower("IŞIK"), "isik")
        self.assertEqual(turkish_lower("ENGLISH"), "english")
        self.assertEqual(normalize_for_matching("KADIKÖY"), normalize_for_matching("kadıköy"))

    def test_turkish_channel_whitelisting(self):
        # Upper case Turkish letters with I / İ should match lowercase custom labels
        self.assertTrue(is_channel_whitelisted("KADIKÖY MÜZİK", custom_labels=["kadıköy müzik"]))
        self.assertTrue(is_channel_whitelisted("İSTANBUL RECORDS", custom_labels=["istanbul records"]))

    def test_utf8_bom_custom_labels(self):
        from core.matcher import load_custom_labels
        import tempfile
        from pathlib import Path

        # Create file with Windows Notepad UTF-8 BOM (\xef\xbb\xbf)
        with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".txt") as tmp:
            tmp.write(b"\xef\xbb\xbfkadikoy_bom_label\nsecond_label\n")
            tmp_path = Path(tmp.name)

        try:
            labels = load_custom_labels(tmp_path, use_cache=False)
            self.assertEqual(labels[0], "kadikoy_bom_label")
            self.assertFalse(labels[0].startswith("\ufeff"))
            self.assertIn("second_label", labels)
        finally:
            tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
