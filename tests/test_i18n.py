import unittest
from core.i18n import get_text, SUPPORTED_LANGUAGES, TRANSLATIONS


class TestI18n(unittest.TestCase):
    def test_supported_languages(self):
        self.assertIn("tr", SUPPORTED_LANGUAGES)
        self.assertIn("en", SUPPORTED_LANGUAGES)

    def test_turkish_translation_retrieval(self):
        title = get_text("card_settings_title", lang="tr")
        self.assertIn("İndirme", title)

    def test_english_translation_retrieval(self):
        title = get_text("card_settings_title", lang="en")
        self.assertIn("Download", title)

    def test_fallback_to_turkish_on_unknown_lang(self):
        text = get_text("card_settings_title", lang="de")
        self.assertIn("İndirme", text)

    def test_parameter_substitution(self):
        tr_res = get_text("adb_connected", lang="tr", device="xyz123")
        self.assertIn("xyz123", tr_res)
        self.assertIn("Bağlı", tr_res)

        en_res = get_text("adb_connected", lang="en", device="xyz123")
        self.assertIn("xyz123", en_res)
        self.assertIn("Connected", en_res)

    def test_missing_key_returns_key_itself(self):
        missing = get_text("completely_unknown_key_999", lang="en")
        self.assertEqual(missing, "completely_unknown_key_999")

    def test_translation_key_parity(self):
        tr_keys = set(TRANSLATIONS["tr"].keys())
        en_keys = set(TRANSLATIONS["en"].keys())
        self.assertEqual(tr_keys, en_keys, f"Missing keys in EN: {tr_keys - en_keys}, Missing in TR: {en_keys - tr_keys}")


if __name__ == "__main__":
    unittest.main()
