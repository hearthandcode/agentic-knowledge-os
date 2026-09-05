"""Consumer enforcement regressions derived from v6 failure categories."""
import copy
import json
import unittest
from pathlib import Path

from agentic_knowledge_os.artifact_contract import compile_request, evaluate_attempts

FIXTURES = Path(__file__).resolve().parents[1] / 'fixtures/evaluation'


class ArtifactContractTests(unittest.TestCase):
    def setUp(self):
        self.request = json.loads((FIXTURES / 'compact-artifact-request.json').read_text())
        self.good = (FIXTURES / 'compact-artifact-valid.json').read_text()
        self.bad = (FIXTURES / 'compact-artifact-invalid.json').read_text()

    def test_valid_source_derived_artifact_reaches_review(self):
        receipt = evaluate_attempts(self.request, [self.good])
        self.assertEqual(receipt['status'], 'valid-candidate')
        self.assertEqual(receipt['artifact_candidate']['content']['mapped_values'], [1.25, None, 4])
        self.assertFalse(receipt['verified'])

    def test_extra_evidence_and_wrappers_are_rejected_without_rewriting(self):
        receipt = evaluate_attempts(self.request, [self.bad])
        self.assertEqual(receipt['status'], 'repair-needed')
        self.assertIsNone(receipt['artifact_candidate'])
        self.assertTrue(any(e['code'] == 'unexpected-properties' for e in receipt['attempts'][0]['diagnostics']))
        self.assertNotIn('The extra wrapper', receipt['repair_prompt'])

    def test_repair_keeps_original_failure_visible(self):
        receipt = evaluate_attempts(self.request, [self.bad, self.good])
        self.assertEqual(receipt['status'], 'valid-candidate')
        self.assertEqual([a['passed'] for a in receipt['attempts']], [False, True])
        self.assertFalse(receipt['first_attempt_passed'])

    def test_budget_exhaustion_never_returns_artifact(self):
        receipt = evaluate_attempts(self.request, [self.bad, self.bad])
        self.assertEqual(receipt['status'], 'exhausted')
        self.assertIsNone(receipt['repair_prompt'])
        with self.assertRaises(ValueError):
            evaluate_attempts(self.request, [self.bad] * 3)

    def test_schema_valid_wrong_calculation_fails_source_check(self):
        data = json.loads(self.good)
        data['artifact']['mapped_values'][0] = 12.5
        receipt = evaluate_attempts(self.request, [json.dumps(data)])
        self.assertEqual(receipt['status'], 'repair-needed')
        self.assertTrue(any(e.get('check_id') == 'first-conversion' for e in receipt['attempts'][0]['diagnostics']))

    def test_types_duplicate_keys_nan_and_empty_artifacts_are_rejected(self):
        bad = [self.good.replace('1.25', 'true'), self.good.replace('1.25', 'NaN'),
               '{"status":"prepared","artifact":{},"artifact":{}}',
               '{"status":"prepared","artifact":{}}', '```json\n' + self.good + '\n```']
        for raw in bad:
            with self.subTest(raw=raw[:50]):
                self.assertIsNone(evaluate_attempts(self.request, [raw])['artifact_candidate'])

    def test_schema_id_refs_are_exact_and_misspellings_fail_closed(self):
        self.request['content_schema']['properties']['source_ids'] = {
            'type': 'array', 'items': {'type': 'string', 'enum': ['duration-input']},
            'minItems': 1, 'maxItems': 1}
        self.request['content_schema']['required'].append('source_ids')
        data = json.loads(self.good)
        data['artifact']['source_ids'] = ['fixture-duration-input']
        self.assertIsNone(evaluate_attempts(self.request, [json.dumps(data)])['artifact_candidate'])

    def test_unsupported_or_open_schema_is_not_silently_ignored(self):
        for field, value in [('patternProperties', {}), ('additionalProperties', True)]:
            request = copy.deepcopy(self.request)
            request['content_schema'][field] = value
            with self.assertRaises(ValueError):
                compile_request(request)

    def test_only_one_role_is_projected(self):
        compiled = compile_request(self.request)
        self.assertLess(compiled['kernel_characters'], 3000)
        self.assertLess(compiled['role_characters'], 1800)
        self.assertNotIn('AKOS-C8-COORD-RFC', compiled['prompt'])
        self.assertNotIn('behavioral-experiment', compiled['prompt'])

    def test_private_data_is_excluded_and_cannot_drive_public_checks(self):
        self.request['sources'].append({'id': 'private-note', 'availability': 'available',
            'sensitivity': 'private', 'authority': 'source', 'data': {'secret': 'SYNTHETIC-PRIVATE'}})
        compiled = compile_request(self.request)
        self.assertNotIn('SYNTHETIC-PRIVATE', json.dumps(compiled))
        self.assertEqual(compiled['source_ledger'][-1]['admission'], 'excluded-for-audience')
        self.request['checks'][0]['source_id'] = 'private-note'
        with self.assertRaises(ValueError):
            compile_request(self.request)

    def test_untrusted_source_remains_evidence_without_authority(self):
        self.request['sources'][0]['authority'] = 'untrusted'
        compiled = compile_request(self.request)
        self.assertEqual(compiled['source_ledger'][0]['admission'], 'included')
        self.assertEqual(compiled['source_ledger'][0]['authority'], 'untrusted')

    def test_hold_and_early_success_are_terminal(self):
        raw = '{"status":"hold","artifact":null,"reason":"Required decision is missing."}'
        result = evaluate_attempts(self.request, [raw])
        self.assertEqual(result['status'], 'held')
        self.assertEqual(result['attempts'][0]['hold_reason'], 'Required decision is missing.')
        self.assertEqual(result['attempts'][0]['checks_applied'], [])
        self.assertIsNone(result['repair_prompt'])
        for attempts in ([raw, self.good], [self.good, self.good]):
            with self.assertRaises(ValueError):
                evaluate_attempts(self.request, attempts)

    def test_impossible_literal_schema_is_rejected(self):
        self.request['checks'] = []
        self.request['content_schema']['properties']['factor']['const'] = 'not a number'
        with self.assertRaises(ValueError):
            compile_request(self.request)

    def test_large_integer_source_copy_does_not_round(self):
        number = 123456789012345678901234567890123456789
        self.request['content_schema']['properties']['factor'] = {'type': 'integer'}
        self.request['sources'][1]['data']['factor'] = number
        output = json.loads(self.good)
        output['artifact']['factor'] = number
        self.assertEqual(evaluate_attempts(self.request, [json.dumps(output)])['status'], 'valid-candidate')

    def test_invalid_unicode_is_rejected_without_fake_byte_identity(self):
        for raw in ('{"status":"hold","artifact":null,"reason":"\\ud800"}', '\ud800'):
            result = evaluate_attempts(self.request, [raw])
            self.assertEqual(result['status'], 'repair-needed')
            self.assertIsNone(result['artifact_candidate'])
        self.assertIsNone(result['attempts'][0]['raw_digest'])

    def test_conflicting_source_checks_are_rejected_before_prompting(self):
        conflicting = copy.deepcopy(self.request['checks'][0])
        conflicting.update(id='contradictory-first-value', factor=0.01)
        self.request['checks'].append(conflicting)
        with self.assertRaisesRegex(ValueError, 'conflicting'):
            compile_request(self.request)


if __name__ == '__main__':
    unittest.main()
