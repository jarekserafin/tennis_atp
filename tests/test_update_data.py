import hashlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError

import update_data


def entry(name, content=b""):
    digest = hashlib.sha1(f"blob {len(content)}\0".encode() + content).hexdigest()
    return {"path": f"atp/{name}", "type": "blob", "sha": digest}


class UpdateDataTests(unittest.TestCase):
    def test_player_height_correction_survives_source_updates_and_skips_unchanged_files(self):
        name = "atp_players.csv"
        header = b"player_id,name_first,name_last,dob,hand,height,wikidata_id\n"
        initial = header + b"106410,Jorge Brian,Panta Herreros,19950722,R,3,Q22007316\n"
        revised = initial.replace(b"Jorge Brian", b"Jorge")
        corrections = {"106410": {"height": 178}}
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            for content in [initial, revised]:
                files = {name: entry(name, content)}
                with patch.object(update_data, "request", return_value=io.BytesIO(content)):
                    update_data.synchronize(destination, files, "revision", corrections=corrections)
                self.assertIn(b",178,", (destination / name).read_bytes())
                with patch.object(update_data, "request") as request:
                    self.assertEqual(update_data.synchronize(destination, files, "revision", corrections=corrections), [])
                    request.assert_not_called()

    def test_unknown_player_correction_preserves_local_data(self):
        name = "atp_players.csv"
        content = b"player_id,name_first,name_last,dob,hand,height,wikidata_id\n1,Test,Player,19900101,R,180,Q1\n"
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            (destination / name).write_bytes(b"original")
            with patch.object(update_data, "request", return_value=io.BytesIO(content)):
                with self.assertRaises(ValueError):
                    update_data.synchronize(destination, {name: entry(name, content)}, "revision", corrections={"missing": {"height": 178}})
            self.assertEqual((destination / name).read_bytes(), b"original")

    def test_selection_keeps_singles_separate_from_other_match_categories(self):
        names = list(update_data.REFERENCE_FILES) + [
            "atp_rankings_current.csv", "atp_rankings_20s.csv", "atp_matches_2026.csv",
            "atp_matches_doubles_2020.csv", "atp_matches_futures_2026.csv",
            "atp_matches_qual_chall_2026.csv", "atp_matches_amateur.csv", "../outside.csv",
        ]
        tree = [entry(name) for name in names]
        tree.append({"path": "LICENSE", "type": "blob", "sha": "license"})
        core = update_data.selected_files(tree)
        self.assertIn("atp_matches_2026.csv", core)
        self.assertNotIn("atp_matches_doubles_2020.csv", core)
        all_files = update_data.selected_files(tree, include_all=True)
        self.assertIn("atp_matches_doubles_2020.csv", all_files)
        self.assertIn("atp_matches_qual_chall_2026.csv", all_files)
        self.assertNotIn("../outside.csv", all_files)

    def test_missing_reference_data_is_rejected(self):
        with self.assertRaises(ValueError):
            update_data.selected_files([entry("atp_matches_2026.csv")])

    def test_check_does_not_create_directory_or_download(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "data"
            with patch.object(update_data, "request") as request:
                changes = update_data.synchronize(destination, {"LICENSE": entry("LICENSE", b"license")}, "commit", check=True)
            self.assertEqual(changes, ["LICENSE"])
            self.assertFalse(destination.exists())
            request.assert_not_called()

    def test_update_then_rerun_skips_unchanged_data(self):
        content = b"ranking_date,rank,player,points\n20260608,1,123,5000\n"
        name = "atp_rankings_current.csv"
        files = {name: entry(name, content)}
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            with patch.object(update_data, "request", return_value=io.BytesIO(content)) as request:
                self.assertEqual(update_data.synchronize(destination, files, "revision"), [name])
                self.assertIn("/revision/atp/", request.call_args.args[0])
            self.assertEqual((destination / name).read_bytes(), content)
            self.assertTrue((destination / ".sackmann-source.json").is_file())
            with patch.object(update_data, "request") as request:
                self.assertEqual(update_data.synchronize(destination, files, "revision"), [])
                request.assert_not_called()

    def test_failed_second_download_preserves_all_existing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            (destination / "LICENSE").write_bytes(b"old license")
            (destination / "UPSTREAM_README.md").write_bytes(b"old readme")
            files = {"LICENSE": entry("LICENSE", b"new license"),
                     "UPSTREAM_README.md": entry("UPSTREAM_README.md", b"new readme")}
            with patch.object(update_data, "request", side_effect=[io.BytesIO(b"new license"), URLError("offline")]):
                with self.assertRaises(URLError):
                    update_data.synchronize(destination, files, "revision")
            self.assertEqual((destination / "LICENSE").read_bytes(), b"old license")
            self.assertEqual((destination / "UPSTREAM_README.md").read_bytes(), b"old readme")
            self.assertFalse((destination / ".sackmann-source.json").exists())
            self.assertFalse(list(destination.glob(".sackmann-download-*")))

    def test_corrupted_or_incompatible_csv_does_not_replace_local_data(self):
        name = "atp_rankings_current.csv"
        for downloaded, expected in [(b"corrupt", b"expected"), (b"unexpected_column\nvalue\n", b"unexpected_column\nvalue\n")]:
            with self.subTest(content=downloaded), tempfile.TemporaryDirectory() as directory:
                destination = Path(directory)
                (destination / name).write_bytes(b"original")
                with patch.object(update_data, "request", return_value=io.BytesIO(downloaded)):
                    with self.assertRaises(ValueError):
                        update_data.synchronize(destination, {name: entry(name, expected)}, "revision")
                self.assertEqual((destination / name).read_bytes(), b"original")


if __name__ == "__main__":
    unittest.main()
