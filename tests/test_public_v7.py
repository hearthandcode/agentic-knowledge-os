import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('verify_public_v7', ROOT / 'scripts/verify_public_v7.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class PublicV7Tests(unittest.TestCase):
    def test_frozen_public_evidence_replays(self):
        self.assertEqual(verifier.verify(ROOT / 'evals/results/v7')['provider_calls'], 0)

    def test_tampered_archive_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'projection'
            shutil.copytree(ROOT / 'evals/results/v7', target)
            with (target / 'frozen-evidence.tar.gz').open('ab') as handle:
                handle.write(b'tampered')
            with self.assertRaisesRegex(ValueError, 'digest mismatch'):
                verifier.verify(target)
