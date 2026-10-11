#!/usr/bin/env python3
"""Offline decisions from explicit observations; no retrieval, authentication or scheduling."""
import argparse
import copy
import datetime
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

SECRET_KEYS = {'password', 'otp', 'cookie', 'cookies', 'sessioncookie', 'apikey',
               'secret', 'accesstoken', 'refreshtoken', 'authorization', 'clientsecret',
               'token', 'idtoken', 'privatekey', 'sessiontoken', 'bearertoken'}

def secret_key(key):
    return isinstance(key, str) and ''.join(c for c in key.lower() if c.isalnum()) in SECRET_KEYS

def contains_secret(value):
    if isinstance(value, dict):
        return any(secret_key(k) or contains_secret(v) for k, v in value.items())
    if isinstance(value, list):
        return any(contains_secret(v) for v in value)
    return False

def classify_access(observation: dict) -> dict:
    """Flags must represent observed evidence. HTTP status alone never proves login."""
    if not isinstance(observation, dict) or contains_secret(observation):
        raise ValueError('Use an observation object without credentials')
    def yes(key):
        return observation.get(key) is True
    def result(status, action, reason):
        return {'status': status, 'action': action, 'reason': reason}
    api_flags = ('api_contract_verified', 'api_permission_verified',
                 'api_entitlement_available', 'api_supports_operation')
    if all(yes(key) for key in api_flags):
        return result('api_available', 'use_official_api', 'All required API checks explicitly verified')
    if yes('public_equivalent_available'):
        return result('public_available', 'use_public_route', 'The same requested record is available publicly')
    if yes('entitlement_required'):
        return result('entitlement_required', 'explain_eligibility', 'Citizen login is not proof of API entitlement')
    if yes('payment_required'):
        return result('payment_required', 'request_payment_authorization', 'Do not start a paid operation implicitly')
    if yes('captcha_required'):
        return result('captcha_required', 'user_complete_captcha', 'CAPTCHA is distinct from authentication')
    if yes('session_expired'):
        return result('login_required', 'reauthenticate_privately', 'Verified authenticated session expired')
    if yes('login_required_for_operation'):
        return result('login_required', 'login_privately', 'Explicit operation-specific authentication barrier')
    if yes('lookup_succeeded') and yes('not_found'):
        return result('not_found', 'report_scoped_lookup', 'Successful lookup reported no matching record')
    if yes('document_inspected'):
        return result('success', 'use_verified_observation', 'Requested original was inspected')
    return result('technical_failure', 'diagnose_or_manual_retrieval', 'Insufficient evidence for login, success, or not-found')

def checked_time(observation):
    value = observation.get('checked_at')
    if not isinstance(value, str):
        return None
    try:
        stamp = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
        return stamp if stamp.tzinfo is not None else None
    except ValueError:
        return None

def comparable(observation):
    return (isinstance(observation, dict) and observation.get('status') == 'success'
            and observation.get('verified') is True
            and isinstance(observation.get('source_id'), str) and observation['source_id'].strip()
            and isinstance(observation.get('item_id'), str) and observation['item_id'].strip()
            and observation.get('content') is not None and checked_time(observation) is not None)

def compare_observation(previous: dict, current: dict) -> dict:
    """Preserve the last successful baseline on failures/insufficient comparable evidence."""
    if contains_secret(previous) or contains_secret(current):
        raise ValueError('Observations must not contain credentials')
    baseline = copy.deepcopy(previous)
    def blocked(reason):
        return {'state': 'blocked', 'baseline': baseline, 'reason': reason}
    if not comparable(current):
        return blocked('Current check lacks successful, verified, timestamped comparable evidence')
    if previous is None:
        return {'state': 'baseline', 'baseline': copy.deepcopy(current)}
    if not comparable(previous):
        return blocked('Previous baseline is not a comparable successful observation')
    if previous['source_id'] != current['source_id']:
        return blocked('Source identity differs')
    if previous['item_id'] != current['item_id']:
        return blocked('Item identity differs')
    if checked_time(current) < checked_time(previous):
        return blocked('Current observation is older than the stored baseline')
    state = 'unchanged' if previous['content'] == current['content'] else 'changed'
    return {'state': state, 'baseline': copy.deepcopy(current)}

def validate_watchlist(data: dict, registry: dict) -> list:
    errors = []
    if not isinstance(data, dict) or not isinstance(registry, dict):
        return ['Watchlist and registry must be objects']
    if contains_secret(data):
        errors.append('Watchlist must not contain credentials')
    if not isinstance(data.get('id'), str) or not data['id'].strip():
        errors.append('Watchlist id required')
    schedule = data.get('schedule', {})
    if not isinstance(schedule, dict) or schedule.get('mode') not in {'manual', 'scheduled'}:
        errors.append('Schedule mode must be manual or scheduled')
    elif schedule['mode'] == 'scheduled':
        try:
            ZoneInfo(schedule.get('timezone') or '')
        except (ValueError, TypeError, ZoneInfoNotFoundError):
            errors.append('Scheduled watchlist requires a valid IANA timezone')
        if not isinstance(schedule.get('frequency'), str) or not schedule['frequency'].strip():
            errors.append('Scheduled watchlist requires frequency')
    rows = registry.get('sources', [])
    if not isinstance(rows, list):
        return errors + ['Registry sources must be an array']
    available = {row.get('id') for row in rows if isinstance(row, dict)
                 and row.get('enabled') is True and row.get('official') is True
                 and row.get('verification_status') in ('page_inspected', 'directory_linked', 'official_index_found')
                 and isinstance(row.get('id'), str)}
    items = data.get('items', [])
    if not isinstance(items, list):
        return errors + ['Watchlist items must be an array']
    for item in items:
        if not isinstance(item, dict):
            errors.append('Watchlist item must be an object')
            continue
        if item.get('type') not in {'case', 'statute', 'topic'}:
            errors.append('Watchlist item type must be case, statute, or topic')
        source_ids = item.get('source_ids')
        if not isinstance(source_ids, list) or not source_ids:
            errors.append('Watchlist item requires source_ids')
            continue
        for sid in source_ids:
            if not isinstance(sid, str) or sid not in available:
                errors.append('Watchlist references an unavailable source')
    return errors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['access', 'compare', 'validate-watchlist'])
    parser.add_argument('--registry', type=Path, default=Path(__file__).resolve().parents[1] / 'references/sources.json')
    args = parser.parse_args()
    try:
        data = json.load(sys.stdin)
        if args.operation == 'access':
            output = classify_access(data)
        elif args.operation == 'compare':
            if not isinstance(data, dict):
                raise ValueError('Comparison input must be an object')
            output = compare_observation(data.get('previous'), data.get('current'))
        else:
            findings = validate_watchlist(data, json.loads(args.registry.read_text(encoding='utf-8')))
            output = {'valid': not findings, 'errors': findings}
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 1 if args.operation == 'validate-watchlist' and not output['valid'] else 0
    except (OSError, ValueError, TypeError) as exc:
        # Report the class, never stringify input/parsing exceptions that may contain secrets.
        print(json.dumps({'error': 'Invalid input; supply secret-free JSON matching the documented operation.'}))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
