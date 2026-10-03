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

    def test_sanitize_filename_max_length_truncation(self):
        long_title = "A" * 200
        sanitized = sanitize_filename(long_title, max_length=120)
        self.assertEqual(len(sanitized), 120)
        self.assertEqual(sanitized, "A" * 120)

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


class TestDownloaderExecution(unittest.TestCase):
    from unittest.mock import patch, MagicMock

    @patch("subprocess.Popen")
    def test_download_playlist_parsing_and_stats(self, mock_popen):
        from unittest.mock import MagicMock
        from core.downloader import SpotVaultDownloader

        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = [
            "Processing query: Daft Punk - One More Time\n",
            'Downloaded "Daft Punk - One More Time"\n',
            "Processing query: Daft Punk - Aerodynamic\n",
            'Skipping "Daft Punk - Aerodynamic" (already exists)\n',
            ""
        ]
        mock_process.poll.return_value = 0
        mock_process.wait.return_value = 0
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        with tempfile.TemporaryDirectory() as tmpdir:
            config = SpotVaultConfig(output_dir=tmpdir, storage_mode="standalone")
            downloader = SpotVaultDownloader(config)
            stats = downloader.download_playlist("https://open.spotify.com/playlist/test", playlist_name="DaftPunk")

            self.assertEqual(stats["downloaded"], 1)
            self.assertEqual(stats["skipped"], 1)
            self.assertEqual(stats["failed"], 0)

    @patch("subprocess.Popen")
    def test_download_playlist_cancellation(self, mock_popen):
        from unittest.mock import MagicMock
        from core.downloader import SpotVaultDownloader

        with tempfile.TemporaryDirectory() as tmpdir:
            config = SpotVaultConfig(output_dir=tmpdir)
            downloader = SpotVaultDownloader(config)

            mock_process = MagicMock()
            def readline_generator():
                downloader.cancel()
                yield "Processing query: Long Track\n"
                yield ""

            gen = readline_generator()
            mock_process.stdout.readline.side_effect = lambda: next(gen, "")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            downloader.download_playlist("https://open.spotify.com/playlist/test")
            self.assertTrue(downloader.cancel_requested)
            mock_process.terminate.assert_called()


if __name__ == "__main__":
    unittest.main()
