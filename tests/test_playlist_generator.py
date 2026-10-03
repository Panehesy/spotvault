import unittest
import tempfile
from pathlib import Path
from core.playlist_generator import generate_all_playlists, write_playlist_file, generate_m3u8_content


class TestPlaylistGenerator(unittest.TestCase):
    def test_empty_directory_handling(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir)
            created = generate_all_playlists(output_dir=out_path, storage_mode="standalone")
            self.assertEqual(len(created), 0)

    def test_m3u8_generation(self):
        tracks = [
            {"artist": "Artist 1", "title": "Song 1", "duration": 180, "relative_path": "song1.mp3"},
            {"artist": "Artist 2", "title": "Song 2", "duration": 210, "relative_path": "song2.m4a"}
        ]
        content = generate_m3u8_content(tracks)
        self.assertIn("#EXTM3U", content)
        self.assertIn("#EXTINF:180,Artist 1 - Song 1", content)
        self.assertIn("song1.mp3", content)
        self.assertIn("song2.m4a", content)

    def test_write_playlist_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "test.m3u8"
            tracks = [{"artist": "Test", "title": "Track", "duration": 120, "filename": "t.mp3"}]
            created = write_playlist_file(target, tracks)
            self.assertTrue(created.exists())
            self.assertIn("Test - Track", created.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
