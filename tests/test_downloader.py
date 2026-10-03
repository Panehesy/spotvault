import unittest
import tempfile
from pathlib import Path
from core.config import SpotVaultConfig
from core.downloader import sanitize_filename, is_track_already_downloaded, build_spotdl_command, reconcile_pool_tracks


class TestDownloaderHelpers(unittest.TestCase):
    def test_reconcile_pool_tracks_includes_cached_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pool_dir = Path(tmpdir) / "Pool"
            pool_dir.mkdir()
            # 2 pre-existing tracks in Pool
            (pool_dir / "Daft Punk - One More Time.mp3").write_bytes(b"data1")
            (pool_dir / "Maft - Harder Better.mp3").write_bytes(b"data2")

            queries = ["Daft Punk - One More Time", "Maft - Harder Better", "New Artist - Missing Track"]
            matched = reconcile_pool_tracks(pool_dir, queries, audio_format="mp3")

            self.assertIn("Daft Punk - One More Time.mp3", matched)
            self.assertIn("Maft - Harder Better.mp3", matched)
            self.assertNotIn("New Artist - Missing Track.mp3", matched)
            self.assertEqual(len(matched), 2)

    def test_sanitize_filename_strips_invalid_chars(self):
        self.assertEqual(sanitize_filename("AC/DC: Back in Black?"), "AC_DC_ Back in Black_")
        self.assertEqual(sanitize_filename("Track <1> *test*"), "Track _1_ _test_")
        self.assertEqual(sanitize_filename("..."), "Untitled")

    def test_is_track_already_downloaded(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            playlist_folder = out_dir / "Rock"
            playlist_folder.mkdir()
            test_file = playlist_folder / "Artist - Song.mp3"
            test_file.write_bytes(b"dummy")

            self.assertTrue(is_track_already_downloaded(
                output_dir=out_dir,
                playlist_name="Rock",
                artist="Artist",
                title="Song",
                audio_format="mp3",
                storage_mode="standalone"
            ))

            self.assertFalse(is_track_already_downloaded(
                output_dir=out_dir,
                playlist_name="Rock",
                artist="Artist",
                title="NonExistent",
                audio_format="mp3",
                storage_mode="standalone"
            ))

    def test_build_spotdl_command(self):
        config = SpotVaultConfig(
            audio_format="m4a",
            bitrate="auto",
            storage_mode="pool_m3u8",
            embed_artwork=True,
            embed_metadata=True,
            download_lyrics=True
        )
        cmd = build_spotdl_command("https://open.spotify.com/playlist/test", config)
        self.assertIn("download", cmd)
        self.assertIn("--format", cmd)
        self.assertIn("m4a", cmd)
        self.assertIn("--bitrate", cmd)
        self.assertIn("auto", cmd)
        self.assertIn("--generate-lrc", cmd)
        self.assertIn("--only-verified-results", cmd)


if __name__ == "__main__":
    unittest.main()
