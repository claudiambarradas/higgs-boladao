"""Testes locais; mídia sintética, sem contas conectadas nem gerações pagas."""
from __future__ import annotations
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _common import SkillError, probe_video, save_json, reserve_attempt, finish_attempt, load_json
from video_frames import candidate_times, extract, scene_times
from verificar_referencias import validate_prompt
from empacotar_manual import validate_manifest, package
from restaurar_audio import restore
spec = importlib.util.spec_from_file_location("skill_installer", ROOT / "install.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)

class PromptTests(unittest.TestCase):
    def test_labels_valid(self):
        self.assertEqual(validate_prompt("Edite @video1 com @imagem1 e @imagem2. Preserve @video1.", 2), [])
    def test_accents_spaces_and_wrong_language_fail(self):
        for label in ("@vídeo1", "@video 1", "@ video1", "@image1", "@imagem 1", "@imagem0", "@Video1", "@imagem1x"):
            with self.subTest(label=label):
                self.assertTrue(validate_prompt(f"Edite @video1 com @imagem1. {label}", 1))
    def test_missing_and_extra_references(self):
        self.assertTrue(validate_prompt("@video1 @imagem2", 2))
        self.assertTrue(validate_prompt("@video1 @imagem1 @imagem3", 1))
    def test_final_prompt_no_placeholder(self):
        self.assertTrue(validate_prompt("@video1 @imagem1 [INSIRA ROUPA]", 1))
    def test_character_limit(self):
        self.assertTrue(validate_prompt("Edite @video1 com @imagem1", 1, 10))
    def test_single_print_still_requires_image(self):
        self.assertTrue(validate_prompt("@video1", 0))

class UtilityTests(unittest.TestCase):
    def test_uniform_coverage(self):
        values = candidate_times(10, 25, every=2)
        self.assertEqual(values[0], 0)
        self.assertAlmostEqual(values[-1], 9.96)
    def test_count_one_is_midpoint(self):
        self.assertEqual(candidate_times(2, 25, count=1), [.98])
    def test_unknown_fps_does_not_skip_last_second(self):
        self.assertAlmostEqual(candidate_times(10, 0)[-1], 9.96)
    def test_bad_times(self):
        for values in ([-1], [3], [float("nan")]):
            with self.assertRaises(SkillError):
                candidate_times(3, explicit=values)
    def test_duplicate_times_deduplicated(self):
        self.assertEqual(candidate_times(3, explicit=[1, 0, 1]), [0, 1])
    def test_ledger_limit_and_status(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "ledger.json"
            token = reserve_attempt(path, 1, "test", "fake")
            finish_attempt(path, token, "simulated")
            self.assertEqual(load_json(path)["attempts"][0]["status"], "simulated")
            with self.assertRaises(SkillError):
                reserve_attempt(path, 1, "test", "fake")
    def test_install_locations_and_real_copy(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d)
            targets = installer.destinations("both", "user", home=home)
            self.assertEqual(targets[0], home / ".claude/skills/higgs-boladao")
            self.assertEqual(targets[1], home / ".agents/skills/higgs-boladao")
            for target in targets:
                installer.copy_skill(ROOT, target, dry_run=True)
                self.assertFalse(target.exists())
                installer.copy_skill(ROOT, target)
                self.assertTrue((target / "SKILL.md").is_file())
                self.assertTrue((target / "scripts/video_frames.py").is_file())
                self.assertFalse((target / ".env").exists())
                with self.assertRaises(ValueError):
                    installer.copy_skill(ROOT, target)
    def test_install_update_backup_outside_skills(self):
        with tempfile.TemporaryDirectory() as d:
            target = installer.destinations("codex", "user", home=Path(d))[0]
            installer.copy_skill(ROOT, target)
            installer.copy_skill(ROOT, target, force=True)
            self.assertEqual(len(list(target.parent.glob("*/SKILL.md"))), 1)
            self.assertEqual(len(list((target.parent.parent / "skill-backups").glob("*/SKILL.md"))), 1)

@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg/FFprobe necessários")
class MediaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = tempfile.TemporaryDirectory()
        cls.root = Path(cls.work.name)
        cls.video = cls.root / "original.mp4"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", "testsrc2=size=180x320:rate=25",
            "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100",
            "-t", "2.4", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
            "-threads", "1", str(cls.video)], check=True, timeout=30)
        cls.meta = probe_video(cls.video)
        cls.frames = cls.root / "frames"
        cls.extracted = extract(cls.video, cls.frames, [0, 1, 2.32], cls.meta)
    @classmethod
    def tearDownClass(cls):
        cls.work.cleanup()
    def setUp(self):
        self.case = Path(tempfile.mkdtemp(dir=self.root))
    def manifest(self):
        original = self.frames / self.extracted["frames"][0]["file"]
        edited = self.case / "edited.png"
        with Image.open(original) as image:
            image = image.convert("RGB")
            image.paste((30, 60, 160), (50, 150, 130, 280))
            image.save(edited)
        prompt = self.case / "prompt.txt"
        prompt.write_text("Edite @video1 usando o visual de @imagem1. Preserve os movimentos e a identidade.", encoding="utf8")
        manifest = {"schema_version":1, "requested_change":"Teste sintético de mudança de roupa",
            "video": str(self.video), "prompt_file":str(prompt),
            "analysis":{"method":"temporal_sampling","duration_seconds":self.meta["duration_seconds"],
                        "full_timeline_reviewed": True,"notes":"Revisão sintética para testar o software; não é avaliação estética."},
            "video_model":{"id":"synthetic_test_only", "schema_verified":True,
                        "verification_note":"Modelo fictício apenas do teste offline", "max_reference_images":3,
                        "max_prompt_chars":1000, "parameters":{}},
            "images":[{"label":"@imagem1","file":str(edited),"source_frame":str(original),
                        "timestamp_seconds":0,"role":"frente","visual_review_passed":True,
                        "review_notes":"Alteração sintética de pixels para testar validações."}]}
        path = self.case / "manifest.json"
        save_json(path, manifest)
        return path, manifest
    def test_probe_audio_ratio_duration(self):
        self.assertTrue(self.meta["has_audio"])
        self.assertEqual(self.meta["aspect_ratio"], "9:16")
        self.assertAlmostEqual(self.meta["duration_seconds"], 2.4, places=1)
    def test_extraction_files_and_contact_sheet(self):
        self.assertEqual(len(self.extracted["frames"]), 3)
        self.assertTrue((self.frames / "analise-001.jpg").is_file())
        self.assertFalse(self.extracted["analysis_complete"])
        for item in self.extracted["frames"]:
            with Image.open(self.frames / item["file"]) as im:
                self.assertEqual(im.size, (180, 320))
    def test_refuses_overwrite_frames(self):
        with self.assertRaises(SkillError):
            extract(self.video, self.frames, [0], self.meta)
    def test_rotation_metadata(self):
        rotated = self.case / "rotated.mp4"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-display_rotation:v:0", "90", "-i", str(self.video),
                        "-c", "copy", str(rotated)], check=True, timeout=30)
        data = probe_video(rotated)
        self.assertEqual(data["aspect_ratio"], "16:9")
        self.assertEqual(data["display_width"], 320)
    def test_scene_scan_completes(self):
        self.assertIsInstance(scene_times(self.video, .3, 30), list)
    def test_manual_package_real_images_prompt_and_map(self):
        path, data = self.manifest()
        out = self.case / "delivery"
        report = package(path, out)
        self.assertTrue((out / "imagem1.png").is_file())
        self.assertTrue((out / "prompt.txt").is_file())
        self.assertIn("@video1", (out / "MAPA-DE-UPLOAD.md").read_text())
        self.assertFalse((out / "original.mp4").exists())
        with zipfile.ZipFile(report["zip"]) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(len(archive.namelist()), 5)
    def test_original_print_is_not_accepted(self):
        path, data = self.manifest()
        data["images"][0]["file"] = data["images"][0]["source_frame"]
        save_json(path, data)
        with self.assertRaises(SkillError): validate_manifest(path)
    def test_absent_visual_review_is_not_accepted(self):
        path, data = self.manifest()
        data["images"][0]["visual_review_passed"] = False
        save_json(path, data)
        with self.assertRaises(SkillError): validate_manifest(path)
    def test_incomplete_timeline_is_not_accepted(self):
        path, data = self.manifest()
        data["analysis"]["full_timeline_reviewed"] = False
        save_json(path, data)
        with self.assertRaises(SkillError): validate_manifest(path)
    def test_wrong_ratio_needs_approval(self):
        path, data = self.manifest()
        Image.new("RGB", (200,200), "red").save(data["images"][0]["file"])
        with self.assertRaises(SkillError): validate_manifest(path)
        data["images"][0].update(aspect_adaptation_approved=True, aspect_adaptation_note="Aprovada no teste sintético")
        save_json(path,data)
        self.assertEqual(len(validate_manifest(path)["images"]),1)
    def test_audio_requires_timing_review(self):
        with self.assertRaises(SkillError):
            restore(self.video, self.video, self.case / "audio.mp4", False)
    def test_audio_restore_when_timing_confirmed(self):
        out = self.case / "audio.mp4"
        restore(self.video, self.video, out, True)
        self.assertTrue(probe_video(out)["has_audio"])
