import unittest
from pathlib import Path
import tempfile
from core.config import SpotVaultConfig


class TestSpotVaultConfig(unittest.TestCase):
    def test_default_config(self):
        config = SpotVaultConfig()
        self.assertEqual(config.audio_format, "mp3")
        self.assertEqual(config.bitrate, "320k")
        self.assertEqual(config.storage_mode, "standalone")
        self.assertTrue(config.embed_artwork)
        self.assertTrue(config.embed_metadata)

    def test_invalid_format_raises_error(self):
        with self.assertRaises(ValueError):
            SpotVaultConfig(audio_format="wav")

    def test_invalid_bitrate_raises_error(self):
        with self.assertRaises(ValueError):
            SpotVaultConfig(bitrate="128k")

    def test_invalid_storage_mode_raises_error(self):
        with self.assertRaises(ValueError):
            SpotVaultConfig(storage_mode="unsupported_mode")

    def test_language_config(self):
        # Default is Turkish
        config = SpotVaultConfig()
        self.assertEqual(config.language, "tr")

        # English configuration
        config_en = SpotVaultConfig(language="en")
        self.assertEqual(config_en.language, "en")

        # Invalid language gracefully falls back to default "tr"
        config_invalid = SpotVaultConfig(language="fr")
        self.assertEqual(config_invalid.language, "tr")

    def test_json_roundtrip(self):
        config = SpotVaultConfig(audio_format="m4a", bitrate="auto", storage_mode="pool_m3u8")
        json_data = config.to_json()
        restored = SpotVaultConfig.from_json(json_data)
        self.assertEqual(restored.audio_format, "m4a")
        self.assertEqual(restored.bitrate, "auto")
        self.assertEqual(restored.storage_mode, "pool_m3u8")

    def test_load_nonexistent_returns_defaults(self):
        config = SpotVaultConfig.load("non_existent_file_xyz_123.json")
        self.assertEqual(config.audio_format, "mp3")
        self.assertEqual(config.bitrate, "320k")

    def test_save_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "subfolder" / "config.json"
            config = SpotVaultConfig(audio_format="m4a", bitrate="auto", storage_mode="pool_m3u8")
            config.save(target)
            self.assertTrue(target.exists())
            loaded = SpotVaultConfig.load(target)
            self.assertEqual(loaded.audio_format, "m4a")

    def test_save_invalid_path_raises_ioerror(self):
        config = SpotVaultConfig()
        with self.assertRaises(IOError):
            config.save("invalid_path_\0_null/config.json")


if __name__ == "__main__":
    unittest.main()
