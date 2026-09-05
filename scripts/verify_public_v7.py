#!/usr/bin/env python3
"""Verify public evidence bytes and replay the frozen v7 scorer without provider calls."""
import hashlib
import json
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath


def verify(root):
    manifest = json.loads((root / 'manifest.json').read_text())
    archive = root / 'frozen-evidence.tar.gz'
    if hashlib.sha256(archive.read_bytes()).hexdigest() != manifest['archive_sha256']:
        raise ValueError('archive digest mismatch')
    with tempfile.TemporaryDirectory(prefix='akos-public-v7-') as directory:
        destination = Path(directory)
        with tarfile.open(archive, 'r:gz') as tar:
            members = tar.getmembers()
            names = [m.name for m in members]
            if len(names) != len(set(names)) or set(names) != {'v7/' + name for name in manifest['files']}:
                raise ValueError('archive inventory mismatch')
            for member in members:
                path = PurePosixPath(member.name)
                if not member.isfile() or path.is_absolute() or '..' in path.parts:
                    raise ValueError('unsafe archive member')
                raw = tar.extractfile(member).read()
                if hashlib.sha256(raw).hexdigest() != manifest['files'][member.name[3:]]:
                    raise ValueError('evidence digest mismatch')
                output = destination.joinpath(*path.parts)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(raw)
        frozen = destination / 'v7'
        result = subprocess.run([sys.executable, '-m', 'agentic_knowledge_os.benchmark_v7',
            'score', '--root', str(frozen)], cwd=destination,
            env={**os.environ, 'PYTHONPATH': str(frozen), 'PYTHONDONTWRITEBYTECODE': '1'},
            capture_output=True, text=True, timeout=60, check=True)
        receipt = json.loads(result.stdout)
        if receipt != json.loads((root / 'receipt.json').read_text()):
            raise ValueError('public receipt differs from raw-evidence replay')
        if json.loads((frozen / 'observations.json').read_text()) != json.loads((root / 'observations.json').read_text()):
            raise ValueError('public observations differ from archived source')
    return {'status': 'passed', 'evidence_files': len(names), 'provider_calls': 0,
            'recorded_benchmark_calls': receipt['total_calls'], 'verified': False}


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1] / 'evals/results/v7'), indent=2))
