import unittest
from spotvault import parse_cli_arguments


class TestCliArguments(unittest.TestCase):
    def test_default_launches_gui(self):
        parsed = parse_cli_arguments([])
        self.assertTrue(parsed.gui)

    def test_cli_flag_forces_headless(self):
        parsed = parse_cli_arguments(["--cli", "--url", "https://open.spotify.com/playlist/test"])
        self.assertFalse(parsed.gui)
        self.assertEqual(parsed.url, "https://open.spotify.com/playlist/test")

    def test_url_without_gui_defaults_to_cli(self):
        parsed = parse_cli_arguments(["--url", "https://open.spotify.com/playlist/test"])
        self.assertFalse(parsed.gui)

    def test_explicit_gui_flag(self):
        parsed = parse_cli_arguments(["--gui"])
        self.assertTrue(parsed.gui)

    def test_custom_options(self):
        parsed = parse_cli_arguments([
            "--cli",
            "--format", "m4a",
            "--bitrate", "auto",
            "--storage-mode", "pool_m3u8",
            "--output-dir", "./custom_music"
        ])
        self.assertEqual(parsed.format, "m4a")
        self.assertEqual(parsed.bitrate, "auto")
        self.assertEqual(parsed.storage_mode, "pool_m3u8")
        self.assertEqual(parsed.output_dir, "./custom_music")


if __name__ == "__main__":
    unittest.main()
