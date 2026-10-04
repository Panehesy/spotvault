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

    def test_nonexistent_directory_handling(self):
        non_existent = Path(tempfile.gettempdir()) / "non_existent_spotvault_test_dir_12345"
        if non_existent.exists():
            import shutil
            shutil.rmtree(non_existent)
        created = generate_all_playlists(output_dir=non_existent, storage_mode="standalone")
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

    def test_pool_m3u8_generation_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            pool_dir = out_dir / "Pool"
            pool_dir.mkdir()
            track_file = pool_dir / "Artist - Track.mp3"
            track_file.write_bytes(b"dummy")

            mapping = {"Favorites": ["Artist - Track.mp3"]}
            created = generate_all_playlists(output_dir=out_dir, storage_mode="pool_m3u8", pool_playlist_mapping=mapping)
            self.assertEqual(len(created), 1)
            pl_file = created[0]
            self.assertEqual(pl_file.name, "Favorites.m3u8")
            self.assertEqual(pl_file.parent.name, "Playlists")
            content = pl_file.read_text(encoding="utf-8")
            self.assertIn("../Pool/Artist - Track.mp3", content)

    def test_pool_m3u8_prunes_missing_files(self):
        import json
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            pool_dir = out_dir / "Pool"
            pool_dir.mkdir()
            existing_track = pool_dir / "Artist - Real.mp3"
            existing_track.write_bytes(b"dummy")

            mapping = {"Favorites": ["Artist - Real.mp3", "Artist - Deleted.mp3"]}
            created = generate_all_playlists(output_dir=out_dir, storage_mode="pool_m3u8", pool_playlist_mapping=mapping)
            self.assertEqual(len(created), 1)
            content = created[0].read_text(encoding="utf-8")
            self.assertIn("Artist - Real.mp3", content)
            self.assertNotIn("Artist - Deleted.mp3", content)

            mapping_file = out_dir / "Playlists" / "pool_mapping.json"
            with open(mapping_file, "r", encoding="utf-8") as f:
                saved_mapping = json.load(f)
            self.assertEqual(saved_mapping["Favorites"], ["Artist - Real.mp3"])


if __name__ == "__main__":
    unittest.main()
