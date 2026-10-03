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

    def test_extract_cli_urls_merges_url_and_file(self):
        from spotvault import extract_cli_urls
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "playlists.txt"
            f.write_text("https://open.spotify.com/playlist/from_file # comment\ninvalid_url_junk\nhttps://open.spotify.com/playlist/from_file\n", encoding="utf-8")

            urls = extract_cli_urls(
                single_url="https://open.spotify.com/track/single_url",
                file_path=f
            )
            self.assertEqual(len(urls), 2)
            self.assertEqual(urls[0], "https://open.spotify.com/track/single_url")
            self.assertEqual(urls[1], "https://open.spotify.com/playlist/from_file")


if __name__ == "__main__":
    unittest.main()
