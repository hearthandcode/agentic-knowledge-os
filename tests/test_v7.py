import json
import tempfile
import unittest
import contextlib
import io
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
from agentic_knowledge_os import benchmark_v7 as v7


class V7Tests(unittest.TestCase):
    def test_inventory_and_prompt_parity(self):
        tasks = v7.tasks()
        self.assertEqual(len(tasks), 12)
        self.assertEqual(len({t['request']['profile_id'] for t in tasks}), 8)
        for task in tasks:
            prompts = v7.prompts(task)
            bodies = [p.split('\nSHARED REQUEST\n')[1] for p in prompts.values()]
            self.assertEqual(len(set(bodies)), 1)
            self.assertNotIn('expected', json.loads(bodies[0]))

    def test_exact_scoring_and_independent_failure(self):
        for task in v7.tasks():
            good = json.dumps({'status': 'prepared', 'artifact': task['expected']})
            self.assertTrue(v7.assess(task, [good])['success'])
            self.assertFalse(v7.assess(task, ['{}'])['success'])
        task = v7.tasks()[2]
        wrong = json.dumps({'status': 'prepared', 'artifact': {**task['expected'], 'difference': 999}})
        result = v7.assess(task, [wrong])
        self.assertTrue(result['gate_passed'])
        self.assertFalse(result['success'])
        self.assertFalse(result['repair_allowed'])

    def test_equal_repair_feedback_and_terminal_budget(self):
        task = v7.tasks()[0]
        result = v7.assess(task, ['{}'])
        self.assertTrue(result['repair_allowed'])
        prompts = v7.prompts(task)
        tails = [v7.repair_prompt(p, result).split('\nREPAIR DIAGNOSTICS\n')[1] for p in prompts.values()]
        self.assertEqual(len(set(tails)), 1)
        self.assertFalse(v7.assess(task, ['{}', '{}'])['repair_allowed'])

    def test_incomplete_inventory_is_not_aggregated(self):
        with self.assertRaises(ValueError):
            v7.summarize([])

    def test_freeze_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            v7.prepare(root)
            v7.verify(root)
            (root / 'plan.json').write_text('{}')
            with self.assertRaises(ValueError):
                v7.verify(root)

    def test_full_repair_ceiling_and_single_use(self):
        expected = {t['request']['task']: t['expected'] for t in v7.tasks()}
        calls = []
        def provider(*args, **kwargs):
            prompt = json.loads(kwargs['input'])[0]['content']
            request = json.loads(prompt.split('\nSHARED REQUEST\n')[1].split('\nREPAIR DIAGNOSTICS\n')[0])
            output = '{}' if '\nREPAIR DIAGNOSTICS\n' not in prompt else json.dumps(
                {'status': 'prepared', 'artifact': expected[request['task']]})
            calls.append(prompt)
            return SimpleNamespace(returncode=0, stdout=output.encode(), stderr=b'')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            v7.prepare(root)
            with patch.object(v7, 'PACKAGE', root / 'agentic_knowledge_os'), patch.object(
                v7, 'minimax_auth_status', return_value={'status': 'ready'}), patch.object(
                v7.subprocess, 'run', side_effect=provider), contextlib.redirect_stdout(io.StringIO()):
                v7.run(root)
                with self.assertRaises(FileExistsError):
                    v7.run(root)
            self.assertEqual(len(calls), 72)
            receipt = json.loads((root / 'receipt.json').read_text())
            self.assertEqual(receipt['metrics']['compact-akos']['first_success'], 0)
            self.assertEqual(receipt['metrics']['compact-akos']['final_success'], 12)
