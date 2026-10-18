"""Regression tests for preserving subtitle evidence and safe transcript output."""
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "parse_vtt.py"
SPEC = importlib.util.spec_from_file_location("parse_vtt", SCRIPT)
vtt = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(vtt)

SAMPLE = "WEBVTT\n\n00:00:01.125 --> 00:00:02.250\nHello\n"


class CueParsingTests(unittest.TestCase):
    def test_keeps_numeric_and_repeated_cues_with_their_own_times(self):
        content = (
            "WEBVTT\n\n1\n00:00.123 --> 00:01.456\n42\n\n"
            "2\n00:02.000 --> 00:03.000\nAgain\n\n"
            "3\n00:04.000 --> 00:05.000\nAgain\n"
        )
        self.assertEqual(vtt.parse_vtt(content), "42\nAgain\nAgain")
        self.assertEqual(
            vtt.parse_vtt(content, keep_timestamps=True),
            "[00:00] 42\n[00:02] Again\n[00:04] Again",
        )

    def test_preserves_identifiers_settings_precision_and_raw_payload(self):
        content = (
            "\ufeffWEBVTT bilingual\r\nKind: captions\r\nLanguage: en\r\n\r\n"
            "speaker-雪\r\n01:02:03.004 --> 01:02:04.987 align:start position:10%\r\n"
            " <v Laurie><b>雪 &amp; AI</b></v>\r\n42 &lt; 100 😀\r\n"
        )
        self.assertEqual(vtt.parse_cues(content), [{
            "id": "speaker-雪",
            "start": "01:02:03.004",
            "end": "01:02:04.987",
            "settings": "align:start position:10%",
            "payload": " <v Laurie><b>雪 &amp; AI</b></v>\r\n42 &lt; 100 😀\r\n",
        }])
        self.assertEqual(vtt.parse_vtt(content), "雪 & AI\n42 < 100 😀")

    def test_skips_complete_note_style_and_region_blocks(self):
        content = (
            "WEBVTT\n\nNOTE source comments\n17\nnot a caption\n\n"
            "STYLE\n::cue { color: lime; }\n\nREGION\nid:region-one\nwidth:40%\n\n"
            "00:01.000 --> 00:02.000\nNOTE is spoken here\n"
        )
        self.assertEqual(vtt.parse_vtt(content), "NOTE is spoken here")

    def test_whitespace_only_payload_lines_do_not_end_a_cue(self):
        content = (
            "WEBVTT\r\n\r\n00:00.640 --> 00:04.309 align:start position:0%\r\n"
            " \r\nOkay.<00:01.199><c> So,</c> hi everyone.\r\n\t\r\n\r\n"
            "00:04.309 --> 00:04.319\r\nOkay. So, hi everyone.\r\n \r\n"
        )
        cues = vtt.parse_cues(content)
        self.assertEqual(len(cues), 2)
        self.assertEqual(
            cues[0]["payload"], " \r\nOkay.<00:01.199><c> So,</c> hi everyone.\r\n\t\r\n",
        )
        self.assertEqual(cues[1]["payload"], "Okay. So, hi everyone.\r\n \r\n")
        self.assertEqual(vtt.parse_vtt(content), "Okay. So, hi everyone.\nOkay. So, hi everyone.")

    def test_inline_timestamp_tags_and_entities_do_not_affect_evidence(self):
        content = "WEBVTT\n\n00:01.000 --> 00:02.000\n<c.green>A</c><00:01.500> &quot;B&quot; &nbsp; C\n"
        self.assertEqual(vtt.parse_vtt(content), 'A "B" \u00a0 C')
        self.assertIn("<00:01.500>", vtt.parse_cues(content)[0]["payload"])

    def test_empty_valid_track_and_long_hours(self):
        self.assertEqual(vtt.parse_cues("WEBVTT\n\n"), [])
        self.assertEqual(vtt.parse_vtt("WEBVTT\n\n"), "")
        self.assertEqual(vtt.display_timestamp("123:45:06.789"), "123:45:06")
        self.assertEqual(vtt.display_timestamp("02:03.004"), "02:03")

    def test_malformed_source_is_reported_instead_of_becoming_prose(self):
        for content in (
            "", "plain text", "WEBVTT\n\nnot a cue\n",
            "WEBVTT\n\n00:99.000 --> 01:00.000\nbad\n",
            "WEBVTT\n\n00:02.000 --> 00:01.000\nbad\n",
            "WEBVTT\n00:01.000 --> 00:02.000\nmissing blank line\n",
        ):
            with self.subTest(content=content):
                with self.assertRaises(ValueError):
                    vtt.parse_vtt(content)

    def test_invalid_types_and_invalid_display_times_are_rejected(self):
        for content in (None, b"WEBVTT", 42):
            with self.subTest(content=content):
                with self.assertRaises(TypeError):
                    vtt.parse_cues(content)
        with self.assertRaises(ValueError):
            vtt.display_timestamp("invalid")

    def test_empty_cue_preserves_evidence_and_legacy_comma_times_work(self):
        content = "WEBVTT\n\n00:01,001 --> 00:02,002\n\n00:02.000 --> 00:03.000\n<b></b>\n"
        self.assertEqual(vtt.parse_cues(content)[0]["payload"], "")
        self.assertEqual(vtt.parse_cues(content)[0]["start"], "00:01,001")
        self.assertEqual(vtt.parse_vtt(content, keep_timestamps=True), "")

    def test_ten_thousand_distinct_cues_are_not_deduplicated(self):
        content = "WEBVTT\n\n" + "\n".join(
            f"{i}\n00:01.000 --> 00:02.000\n42\n" for i in range(10000)
        )
        self.assertEqual(len(vtt.parse_cues(content)), 10000)
        self.assertEqual(vtt.parse_vtt(content).splitlines(), ["42"] * 10000)


class CommandLineTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def write(self, name, content=SAMPLE):
        path = self.root / name
        path.write_bytes(content.encode("utf-8"))
        return path

    def run_cli(self, *args, external=False):
        if external:
            return subprocess.run(
                [sys.executable, str(SCRIPT), *map(str, args)],
                capture_output=True, text=True, check=False,
            )
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                vtt.main(list(map(str, args)))
                code = 0
            except SystemExit as error:
                code = error.code
        return SimpleNamespace(returncode=code, stdout=stdout.getvalue(), stderr=stderr.getvalue())

    def test_file_generates_readable_text_and_lossless_json_without_mutating_source(self):
        content = SAMPLE.replace("\n", "\r\n")
        source = self.write("source.vtt", content)
        before = source.read_bytes()
        result = self.run_cli(source, "--keep-timestamps", external=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(source.read_bytes(), before)
        self.assertEqual((self.root / "source_timestamped.txt").read_text(), "[00:01] Hello")
        cues = json.loads((self.root / "source_cues.json").read_text())
        self.assertEqual(cues[0]["start"], "00:00:01.125")
        self.assertEqual(cues[0]["payload"], "Hello\r\n")

    def test_rejects_non_vtt_even_with_overwrite(self):
        source = self.write("source.txt", "original text")
        result = self.run_cli(source, "--overwrite")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(".vtt", result.stderr)
        self.assertEqual(source.read_text(), "original text")

    def test_existing_output_requires_explicit_overwrite(self):
        source = self.write("source.vtt")
        output = self.write("source_parsed.txt", "keep me")
        rejected = self.run_cli(source)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("--overwrite", rejected.stderr)
        self.assertEqual(output.read_text(), "keep me")
        self.assertFalse((self.root / "source_cues.json").exists())
        accepted = self.run_cli(source, "--overwrite")
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertEqual(output.read_text(), "Hello")

    def test_existing_json_also_blocks_text_output(self):
        source = self.write("source.vtt")
        output = self.write("source_cues.json", "keep evidence")
        result = self.run_cli(source)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(output.read_text(), "keep evidence")
        self.assertFalse((self.root / "source_parsed.txt").exists())

    def test_batch_preflights_all_files_before_writing(self):
        self.write("a.vtt")
        self.write("b.vtt")
        self.write("b_cues.json", "keep evidence")
        result = self.run_cli(self.root)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / "a_parsed.txt").exists())
        self.assertFalse((self.root / "a_cues.json").exists())

    def test_batch_parses_all_files_before_writing(self):
        self.write("a.vtt")
        self.write("b.vtt", "WEBVTT\n\nbroken timing\n")
        result = self.run_cli(self.root / "*.vtt")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("b.vtt", result.stderr)
        self.assertFalse((self.root / "a_parsed.txt").exists())

    def test_output_alias_of_input_is_rejected_even_with_overwrite(self):
        source = self.write("source.vtt")
        (self.root / "source_parsed.txt").symlink_to(source)
        result = self.run_cli(source, "--overwrite")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("input", result.stderr)
        self.assertEqual(source.read_text(), SAMPLE)

    def test_hard_link_to_input_is_also_protected(self):
        source = self.write("source.vtt")
        os.link(source, self.root / "source_cues.json")
        result = self.run_cli(source, "--overwrite")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("input", result.stderr)
        self.assertEqual(source.read_text(), SAMPLE)

    def test_existing_directory_and_output_aliases_are_rejected(self):
        source = self.write("source.vtt")
        output = self.root / "source_parsed.txt"
        output.mkdir()
        result = self.run_cli(source, "--overwrite")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("directory", result.stderr)
        output.rmdir()
        output.write_text("keep")
        (self.root / "source_cues.json").symlink_to(output)
        result = self.run_cli(source, "--overwrite")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("collide", result.stderr)
        self.assertEqual(output.read_text(), "keep")

    def test_invalid_utf8_does_not_create_outputs(self):
        source = self.root / "source.vtt"
        source.write_bytes(b"\xff\xfe")
        result = self.run_cli(source)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source.vtt", result.stderr)
        self.assertEqual(list(self.root.iterdir()), [source])

    def test_directory_accepts_uppercase_vtt_and_timestamp_mode(self):
        self.write("source.VTT")
        result = self.run_cli(self.root, "--keep-timestamps")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / "source_timestamped.txt").read_text(), "[00:01] Hello")

    def test_literal_existing_filename_with_glob_characters_is_supported(self):
        source = self.write("Workshop [SHMCGrNJJGc].en.vtt")
        result = self.run_cli(source)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (self.root / "Workshop [SHMCGrNJJGc].en_parsed.txt").read_text(), "Hello",
        )
        self.assertTrue((self.root / "Workshop [SHMCGrNJJGc].en_cues.json").exists())
        self.assertEqual(source.read_text(), SAMPLE)

    def test_vtt_named_directory_is_rejected_in_batch(self):
        (self.root / "directory.vtt").mkdir()
        result = self.run_cli(self.root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Only .vtt input files", result.stderr)

    def test_glob_with_non_vtt_does_not_overwrite_any_inputs(self):
        self.write("a.vtt")
        text = self.write("b.txt", "important")
        result = self.run_cli(self.root / "*")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(text.read_text(), "important")
        self.assertFalse((self.root / "a_parsed.txt").exists())

    def test_empty_directory_has_clear_nonzero_error(self):
        result = self.run_cli(self.root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("No VTT files", result.stderr)


if __name__ == "__main__":
    unittest.main()
