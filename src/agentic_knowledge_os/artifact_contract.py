"""Compact prompt compilation and fail-closed candidate gating; no providers or writes.

Content schemas support a deliberately bounded JSON Schema subset. Unknown keywords
are errors. Checks bind consumer JSON pointers to copy/scale operations on admitted
source data. Neither shape checks nor declared invariants establish semantic acceptance.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from decimal import Decimal, localcontext
from importlib.resources import files
from pathlib import PurePosixPath

from .compiler import core8_profiles

REQUEST_FIELDS = {'schema', 'task', 'artifact_path', 'profile_id', 'audience', 'max_attempts',
                  'content_schema', 'sources', 'checks'}
SOURCE_FIELDS = {'id', 'availability', 'sensitivity', 'authority', 'data'}
BASE_CHECK_FIELDS = {'id', 'target', 'source_id', 'source_pointer', 'operation'}
TYPE_KEYWORDS = {
    'object': {'properties', 'required', 'additionalProperties'},
    'array': {'items', 'minItems', 'maxItems', 'uniqueItems'},
    'string': {'minLength', 'maxLength'},
    'number': {'minimum', 'maximum'},
    'integer': {'minimum', 'maximum'},
    'boolean': set(), 'null': set(),
}
COMMON_KEYWORDS = {'type', 'enum', 'const', 'description', 'title'}


def canonical(value):
    rendered = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
    rendered.encode('utf-8')  # reject unpaired surrogates, including escaped JSON input
    return rendered


def byte_digest(value: bytes):
    return 'sha256:' + hashlib.sha256(value).hexdigest()


def _number(value):
    return type(value) is int or (type(value) is float and math.isfinite(value))


def _equal(left, right):
    if _number(left) and _number(right):
        return Decimal(str(left)) == Decimal(str(right))
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return set(left) == set(right) and all(_equal(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(_equal(a, b) for a, b in zip(left, right))
    return left == right


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result

    def invalid_constant(_value):
        raise ValueError('non-finite JSON number')

    value = json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid_constant)
    canonical(value)  # also rejects finite-looking literals that overflow to infinity
    return value


def _types(schema):
    value = schema.get('type')
    types = [value] if isinstance(value, str) else value
    if not isinstance(types, list) or not types or any(not isinstance(t, str) or t not in TYPE_KEYWORDS for t in types):
        raise ValueError('schema requires supported explicit types')
    if len(types) != len(set(types)) or len([t for t in types if t != 'null']) > 1:
        raise ValueError('only one type plus optional null is supported')
    return types


def validate_content_schema(schema, depth=0):
    if not isinstance(schema, dict) or depth > 16:
        raise ValueError('invalid or excessively deep content schema')
    types = _types(schema)
    allowed = COMMON_KEYWORDS | set().union(*(TYPE_KEYWORDS[t] for t in types))
    if set(schema) - allowed:
        raise ValueError('unsupported content schema keyword')
    for key in ('description', 'title'):
        if key in schema and not isinstance(schema[key], str):
            raise ValueError('schema annotation must be a string')
    if 'object' in types:
        properties, required = schema.get('properties'), schema.get('required')
        if schema.get('additionalProperties') is not False or not isinstance(properties, dict):
            raise ValueError('every object schema must be closed')
        if not isinstance(required, list) or any(not isinstance(k, str) for k in required):
            raise ValueError('object schema requires explicit fields')
        if set(required) != set(properties) or len(required) != len(set(required)):
            raise ValueError('all consumer properties must be required; use explicit nullable types')
        for child in properties.values():
            validate_content_schema(child, depth + 1)
    if 'array' in types:
        validate_content_schema(schema.get('items'), depth + 1)
        if 'uniqueItems' in schema and type(schema['uniqueItems']) is not bool:
            raise ValueError('uniqueItems must be boolean')
    for lower, upper in (('minItems', 'maxItems'), ('minLength', 'maxLength'), ('minimum', 'maximum')):
        for key in (lower, upper):
            if key in schema:
                value = schema[key]
                if not _number(value) or (key not in ('minimum', 'maximum') and (type(value) is not int or value < 0)):
                    raise ValueError('invalid schema bound')
        if lower in schema and upper in schema and schema[lower] > schema[upper]:
            raise ValueError('contradictory schema bounds')
    if 'enum' in schema:
        values = schema['enum']
        if not isinstance(values, list) or not values or any(_equal(v, earlier) for i, v in enumerate(values) for earlier in values[:i]):
            raise ValueError('enum must contain distinct JSON values')
    canonical(schema)
    without_literals = {k: v for k, v in schema.items() if k not in ('const', 'enum')}
    literals = ([schema['const']] if 'const' in schema else []) + schema.get('enum', [])
    if any(content_errors(value, without_literals) for value in literals):
        raise ValueError('schema literal conflicts with its declared constraints')
    if 'const' in schema and 'enum' in schema and not any(_equal(schema['const'], v) for v in schema['enum']):
        raise ValueError('const is excluded by enum')


def _matches(value, kind):
    return {'object': lambda: isinstance(value, dict), 'array': lambda: isinstance(value, list),
            'string': lambda: isinstance(value, str), 'number': lambda: _number(value),
            'integer': lambda: type(value) is int or (type(value) is float and math.isfinite(value) and value.is_integer()),
            'boolean': lambda: type(value) is bool, 'null': lambda: value is None}[kind]()


def _escape(key):
    return str(key).replace('~', '~0').replace('/', '~1')


def content_errors(value, schema, pointer='/artifact'):
    errors = []

    def error(code):
        errors.append({'pointer': pointer, 'code': code})

    if not any(_matches(value, t) for t in _types(schema)):
        error('wrong-type')
        return errors
    if 'const' in schema and not _equal(value, schema['const']):
        error('const-mismatch')
    if 'enum' in schema and not any(_equal(value, item) for item in schema['enum']):
        error('enum-mismatch')
    if isinstance(value, dict):
        properties = schema['properties']
        if set(value) - set(properties):
            error('unexpected-properties')  # do not echo untrusted property names into repair instructions
        for key in schema['required']:
            if key not in value:
                errors.append({'pointer': pointer + '/' + _escape(key), 'code': 'missing-property'})
        for key in properties:
            if key in value:
                errors.extend(content_errors(value[key], properties[key], pointer + '/' + _escape(key)))
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0) or len(value) > schema.get('maxItems', float('inf')):
            error('array-length')
        if schema.get('uniqueItems') and any(_equal(v, p) for i, v in enumerate(value) for p in value[:i]):
            error('duplicate-items')
        for i, item in enumerate(value):
            errors.extend(content_errors(item, schema['items'], pointer + '/' + str(i)))
    if isinstance(value, str) and (len(value) < schema.get('minLength', 0) or len(value) > schema.get('maxLength', float('inf'))):
        error('string-length')
    if _number(value) and (value < schema.get('minimum', -float('inf')) or value > schema.get('maximum', float('inf'))):
        error('number-range')
    return errors


def _pointer_parts(pointer):
    if not isinstance(pointer, str) or (pointer and not pointer.startswith('/')) or re.search(r'~(?![01])', pointer):
        raise ValueError('invalid JSON pointer')
    return [part.replace('~1', '/').replace('~0', '~') for part in pointer[1:].split('/')] if pointer else []


def _at(value, pointer):
    for part in _pointer_parts(pointer):
        if isinstance(value, dict) and part in value:
            value = value[part]
        elif isinstance(value, list) and re.fullmatch(r'0|[1-9][0-9]*', part) and int(part) < len(value):
            value = value[int(part)]
        else:
            raise ValueError('JSON pointer does not resolve')
    return value


def _schema_at(schema, pointer):
    for part in _pointer_parts(pointer):
        if 'object' in _types(schema) and part in schema['properties']:
            schema = schema['properties'][part]
        elif 'array' in _types(schema) and re.fullmatch(r'0|[1-9][0-9]*', part):
            if int(part) >= schema.get('maxItems', float('inf')):
                raise ValueError('check target exceeds schema array bound')
            schema = schema['items']
        else:
            raise ValueError('check target is not declared by consumer schema')
    return schema


def _source_value(check, sources):
    value = _at(sources[check['source_id']]['data'], check['source_pointer'])
    if check['operation'] == 'scale':
        if not _number(value):
            raise ValueError('scale requires a numeric source; preserve null using copy')
        left, right = Decimal(str(value)), Decimal(str(check['factor']))
        with localcontext() as context:
            context.prec = max(28, len(left.as_tuple().digits) + len(right.as_tuple().digits))
            return left * right
    return value


def _validate_request(request):
    if not isinstance(request, dict) or set(request) != REQUEST_FIELDS or request['schema'] != 'akos.artifact-request.v1':
        raise ValueError('open or unsupported artifact request')
    canonical(request)
    if not isinstance(request['task'], str) or not request['task'].strip():
        raise ValueError('request task is required')
    path = request['artifact_path']
    if not isinstance(path, str) or not path or '\\' in path or any(ord(c) < 32 for c in path):
        raise ValueError('invalid consumer path')
    if PurePosixPath(path).is_absolute() or any(p in ('', '.', '..') for p in path.split('/')):
        raise ValueError('consumer path must be a normalized relative locator')
    if request['audience'] not in ('public', 'private') or type(request['max_attempts']) is not int or not 1 <= request['max_attempts'] <= 2:
        raise ValueError('invalid audience or attempt ceiling')
    profiles = {p['id']: p for p in core8_profiles()}
    selected = request['profile_id']
    if selected is not None and (not isinstance(selected, str) or selected not in profiles):
        raise ValueError('unknown selected profile')
    validate_content_schema(request['content_schema'])
    if request['content_schema']['type'] != 'object':
        raise ValueError('consumer root must be an object')
    if not isinstance(request['sources'], list):
        raise ValueError('source list required')
    sources, ledger = {}, []
    for source in request['sources']:
        if not isinstance(source, dict) or set(source) != SOURCE_FIELDS:
            raise ValueError('open source record')
        identifier = source['id']
        if not isinstance(identifier, str) or not identifier or identifier in sources:
            raise ValueError('invalid or duplicate source identifier')
        if source['availability'] not in ('available', 'unavailable') or source['sensitivity'] not in ('public', 'private') or source['authority'] not in ('source', 'decision', 'untrusted', 'unknown'):
            raise ValueError('unsupported source classification')
        if source['availability'] == 'unavailable' and source['data'] is not None:
            raise ValueError('unavailable source cannot contain supplied data')
        admission = ('unavailable' if source['availability'] == 'unavailable' else
                     'excluded-for-audience' if request['audience'] == 'public' and source['sensitivity'] == 'private' else 'included')
        sources[identifier] = source
        ledger.append({'source_id': identifier, 'admission': admission, 'authority': source['authority']})
    admitted = {entry['source_id'] for entry in ledger if entry['admission'] == 'included'}
    if not isinstance(request['checks'], list):
        raise ValueError('checks must be a list')
    ids, target_values = set(), {}
    for check in request['checks']:
        if not isinstance(check, dict) or check.get('operation') not in ('copy', 'scale'):
            raise ValueError('unsupported source check')
        if set(check) != BASE_CHECK_FIELDS | ({'factor'} if check['operation'] == 'scale' else set()):
            raise ValueError('open source check')
        if not isinstance(check['id'], str) or not check['id'] or check['id'] in ids:
            raise ValueError('invalid or duplicate check ID')
        ids.add(check['id'])
        if not isinstance(check['source_id'], str) or check['source_id'] not in admitted:
            raise ValueError('check depends on unknown, unavailable or audience-excluded source')
        if check['operation'] == 'scale' and not _number(check['factor']):
            raise ValueError('scale factor must be finite')
        target_schema = _schema_at(request['content_schema'], check['target'])
        expected = _source_value(check, sources)
        comparable = Decimal(str(expected)) if _number(expected) else expected
        if check['target'] in target_values:
            previous = target_values[check['target']]
            equal = (previous == comparable if isinstance(previous, Decimal) and isinstance(comparable, Decimal)
                     else type(previous) is type(comparable) and _equal(previous, comparable))
            if not equal:
                raise ValueError('conflicting source checks for the same target')
        target_values[check['target']] = comparable
        if isinstance(expected, Decimal):
            expected = int(expected) if expected == expected.to_integral_value() else float(expected)
        if not _number(expected) and isinstance(expected, float):
            raise ValueError('source calculation overflows JSON numeric range')
        if content_errors(expected, target_schema):
            raise ValueError('source check conflicts with consumer schema')
    return profiles.get(selected), sources, ledger


def compile_request(request):
    """Project the short kernel, one role, public contract and only admitted source data."""
    profile, sources, ledger = _validate_request(request)
    kernel = files('agentic_knowledge_os.data').joinpath('compact-runtime-contract.md').read_text()
    role = ({'id': profile['id'], 'owned_outcome': profile['owned_outcome'], 'boundaries': profile['boundaries']}
            if profile else {})
    projected = {k: v for k, v in request.items() if k != 'sources'}
    projected['sources'] = [
        {**entry, **({'data': sources[entry['source_id']]['data']} if entry['admission'] == 'included' else {})}
        for entry in ledger]
    # Source data and authority are separate fields; classification is supplied by the request owner.
    prompt = kernel + '\nSELECTED ROLE\n' + canonical(role) + '\nARTIFACT REQUEST\n' + canonical(projected)
    schema = {'$schema': 'https://json-schema.org/draft/2020-12/schema', 'oneOf': [
        {'type': 'object', 'additionalProperties': False, 'required': ['status', 'artifact'],
         'properties': {'status': {'const': 'prepared'}, 'artifact': request['content_schema']}},
        {'type': 'object', 'additionalProperties': False, 'required': ['status', 'artifact', 'reason'],
         'properties': {'status': {'const': 'hold'}, 'artifact': {'type': 'null'}, 'reason': {'type': 'string', 'minLength': 1}}},
    ]}
    return {'schema': 'akos.compiled-artifact-request.v1', 'request_digest': byte_digest(canonical(projected).encode()),
            'prompt_digest': byte_digest(prompt.encode()), 'prompt': prompt, 'output_schema': schema,
            'source_ledger': ledger, 'kernel_characters': len(kernel), 'role_characters': len(canonical(role)),
            'total_prompt_characters': len(prompt), 'effect': 'none', 'verified': False}


def evaluate_attempts(request, attempts):
    """Gate one initial attempt and at most one replacement. Never coerce candidate bytes."""
    compiled = compile_request(request)
    if not isinstance(attempts, list) or not 1 <= len(attempts) <= request['max_attempts'] or any(not isinstance(raw, str) for raw in attempts):
        raise ValueError('attempt inventory exceeds the declared budget or contains non-text input')
    sources = {s['id']: s for s in request['sources']}
    records, candidate, status = [], None, 'repair-needed'
    for index, raw in enumerate(attempts):
        diagnostics, held, content, checked, hold_reason = [], False, None, [], None
        raw_digest = None
        try:
            raw_bytes = raw.encode('utf-8')
            raw_digest = byte_digest(raw_bytes)
            if len(raw_bytes) > 1_000_000:
                raise ValueError('candidate too large')
            parsed = strict_json(raw)
        except (ValueError, RecursionError):
            parsed = None
            diagnostics.append({'pointer': '', 'code': 'invalid-json'})
        if not diagnostics:
            if isinstance(parsed, dict) and set(parsed) == {'status', 'artifact', 'reason'} and parsed['status'] == 'hold' and parsed['artifact'] is None and isinstance(parsed['reason'], str) and parsed['reason'].strip():
                held = True
                hold_reason = parsed['reason']
            elif not isinstance(parsed, dict) or set(parsed) != {'status', 'artifact'} or parsed['status'] != 'prepared':
                diagnostics.append({'pointer': '', 'code': 'invalid-envelope'})
            else:
                content = parsed['artifact']
                diagnostics.extend(content_errors(content, request['content_schema']))
                if not diagnostics:
                    for check in request['checks']:
                        checked.append(check['id'])
                        try:
                            observed = _at(content, check['target'])
                            expected = _source_value(check, sources)
                            equal = (_number(observed) and Decimal(str(observed)) == expected
                                     if isinstance(expected, Decimal) else _equal(observed, expected))
                        except ValueError:
                            equal = False
                        if not equal:
                            diagnostics.append({'pointer': '/artifact' + check['target'],
                                                'code': 'source-value-mismatch', 'check_id': check['id']})
        passed = not diagnostics and not held
        records.append({'attempt': index + 1, 'raw_digest': raw_digest,
                        'passed': passed, 'held': held, 'hold_reason': hold_reason,
                        'checks_applied': checked, 'diagnostics': diagnostics})
        if passed or held:
            if index != len(attempts) - 1:
                raise ValueError('attempt supplied after terminal success or hold')
            status = 'valid-candidate' if passed else 'held'
            candidate = {'path': request['artifact_path'], 'content': content} if passed else None
            break
    if status == 'repair-needed' and len(attempts) == request['max_attempts']:
        status = 'exhausted'
    repair = None
    if status == 'repair-needed':
        repair = compiled['prompt'] + '\nLOCAL GATE DIAGNOSTICS\n' + canonical(records[-1]['diagnostics'])
        repair += '\nPrepare a replacement under the unchanged contract. This is the final allowed attempt. Return only the JSON envelope.'
    return {'schema': 'akos.artifact-gate-receipt.v1', 'status': status,
            'request_digest': compiled['request_digest'], 'prompt_digest': compiled['prompt_digest'],
            'source_ledger': compiled['source_ledger'], 'attempts': records,
            'first_attempt_passed': records[0]['passed'], 'artifact_candidate': candidate,
            'repair_prompt': repair, 'checks_declared': [c['id'] for c in request['checks']],
            'claim_limit': 'JSON shape and declared source checks only; semantic acceptance and effectiveness unmeasured',
            'review_status': 'review-required', 'verified': False}
