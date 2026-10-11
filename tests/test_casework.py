import copy
import importlib.util
from pathlib import Path
import unittest

HELPER = Path(__file__).resolve().parents[1] / 'plugins/indian-law/skills/indian-law/scripts/casework.py'

class CaseworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('casework', HELPER)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_generic_403_is_not_login(self):
        self.assertEqual(self.module.classify_access({'http_status': 403})['status'], 'technical_failure')

    def test_public_equivalent_avoids_login(self):
        result = self.module.classify_access({'login_required_for_operation': True, 'public_equivalent_available': True})
        self.assertEqual(result['action'], 'use_public_route')

    def test_needed_explicit_login(self):
        self.assertEqual(self.module.classify_access({'login_required_for_operation': True})['status'], 'login_required')

    def test_expired_session(self):
        self.assertEqual(self.module.classify_access({'session_expired': True})['action'], 'reauthenticate_privately')

    def test_captcha_is_not_login(self):
        self.assertEqual(self.module.classify_access({'captcha_required': True})['status'], 'captcha_required')

    def test_api_needs_all_verifications(self):
        base = {'api_contract_verified': True, 'api_permission_verified': True,
                'api_entitlement_available': True, 'api_supports_operation': True}
        self.assertEqual(self.module.classify_access(base)['action'], 'use_official_api')
        for key in base:
            with self.subTest(key=key):
                invalid = dict(base, **{key: False})
                self.assertNotEqual(self.module.classify_access(invalid)['action'], 'use_official_api')

    def test_not_found_needs_successful_lookup(self):
        self.assertNotEqual(self.module.classify_access({'not_found': True})['status'], 'not_found')
        self.assertEqual(self.module.classify_access({'lookup_succeeded': True, 'not_found': True})['status'], 'not_found')

    def test_string_true_does_not_establish_access(self):
        self.assertNotEqual(self.module.classify_access({'login_required_for_operation': 'false'})['status'], 'login_required')

    def test_credentials_rejected(self):
        with self.assertRaises(ValueError):
            self.module.classify_access({'password': 'do-not-log'})

    def observation(self, content='hearing-2026-10-12'):
        return {'source_id': 'ecourts-services', 'item_id': 'synthetic-case-1', 'status': 'success',
                'checked_at': '2026-10-10T12:00:00+05:30',
                'content': content, 'verified': True}

    def test_first_success_is_baseline(self):
        result = self.module.compare_observation(None, self.observation())
        self.assertEqual(result['state'], 'baseline')

    def test_comparable_content_unchanged(self):
        result = self.module.compare_observation(self.observation(), self.observation())
        self.assertEqual(result['state'], 'unchanged')

    def test_changed_document_same_url(self):
        old, new = self.observation('old'), self.observation('new')
        old['url'] = new['url'] = 'https://court.gov.in/order.pdf'
        self.assertEqual(self.module.compare_observation(old, new)['state'], 'changed')

    def test_failed_check_keeps_baseline(self):
        old = self.observation()
        snapshot = copy.deepcopy(old)
        result = self.module.compare_observation(old, {'source_id': 'ecourts-services', 'status': 'technical_failure'})
        self.assertEqual(result['state'], 'blocked')
        self.assertEqual(result['baseline'], snapshot)
        self.assertEqual(old, snapshot)

    def test_success_without_evidence_is_blocked(self):
        new = self.observation()
        for key in ('content', 'checked_at', 'verified'):
            with self.subTest(key=key):
                invalid = dict(new)
                invalid.pop(key)
                self.assertEqual(self.module.compare_observation(new, invalid)['state'], 'blocked')

    def test_different_source_not_comparable(self):
        old, new = self.observation(), self.observation()
        new['source_id'] = 'sci-status'
        self.assertEqual(self.module.compare_observation(old, new)['state'], 'blocked')

    def test_different_case_same_source_not_comparable(self):
        old, new = self.observation(), self.observation()
        new['item_id'] = 'synthetic-case-2'
        self.assertEqual(self.module.compare_observation(old, new)['state'], 'blocked')

    def test_item_identity_required_for_baseline(self):
        new = self.observation()
        new.pop('item_id')
        self.assertEqual(self.module.compare_observation(None, new)['state'], 'blocked')

    def test_older_observation_cannot_overwrite_baseline(self):
        old, new = self.observation(), self.observation('new')
        new['checked_at'] = '2026-10-09T12:00:00+05:30'
        result = self.module.compare_observation(old, new)
        self.assertEqual(result['state'], 'blocked')
        self.assertEqual(result['baseline'], old)

    def test_watchlist_rejects_unknown_and_disabled_sources(self):
        registry = {'sources': [{'id': 'ok', 'enabled': True, 'official': True},
                                 {'id': 'private', 'enabled': False, 'official': False}]}
        for source in ['absent', 'private']:
            data = {'id': 'w', 'items': [{'type':'case','source_ids':[source]}],
                    'schedule':{'mode':'manual'}}
            self.assertTrue(self.module.validate_watchlist(data, registry))

    def test_scheduled_watch_needs_valid_timezone_and_frequency(self):
        registry = {'sources': []}
        data = {'id':'w','items':[],'schedule':{'mode':'scheduled','timezone':'not/a/zone','frequency':'daily'}}
        self.assertTrue(self.module.validate_watchlist(data, registry))
        data['schedule']['timezone'] = 'Asia/Kolkata'
        self.assertFalse(self.module.validate_watchlist(data, registry))
        data['schedule']['frequency'] = None
        self.assertTrue(self.module.validate_watchlist(data, registry))

    def test_client_secret_cannot_enter_baseline(self):
        new = self.observation()
        new['client_secret'] = 'synthetic'
        with self.assertRaises(ValueError):
            self.module.compare_observation(None, new)

    def test_token_cannot_enter_watchlist(self):
        data = {'id':'w','items':[],'schedule':{'mode':'manual'}, 'token':'synthetic'}
        self.assertTrue(self.module.validate_watchlist(data, {'sources':[]}))

    def test_watchlist_no_secrets(self):
        data = {'id':'w','items':[],'schedule':{'mode':'manual'},'cookies':{'session':'s'}}
        self.assertTrue(self.module.validate_watchlist(data, {'sources':[]}))

    def test_nested_camel_case_credentials_rejected(self):
        for key in ('clientSecret', 'session_token', 'private-key'):
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.module.classify_access({'nested': {key: 'synthetic'}})

    def test_unverified_source_cannot_enter_watchlist(self):
        registry = {'sources': [{'id':'candidate','enabled':True,'official':True,
                                 'verification_status':'candidate_unverified'}]}
        watch = {'id':'w','schedule':{'mode':'manual'},
                 'items':[{'type':'case','source_ids':['candidate']}]}
        self.assertTrue(self.module.validate_watchlist(watch, registry))

    def test_cli_does_not_echo_credential_input(self):
        import subprocess
        import json
        observation = self.observation()
        observation['clientSecret'] = 'SYNTHETIC_MUST_NOT_ECHO'
        result = subprocess.run(['python3', str(HELPER), 'compare'],
                                input=json.dumps({'previous':None,'current':observation}),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn('SYNTHETIC_MUST_NOT_ECHO', result.stdout + result.stderr)

    def test_source_identity_must_be_nonblank_string(self):
        for value in ([], {'id':'case'}, True, ''):
            with self.subTest(value=value):
                new = self.observation()
                new['source_id'] = value
                self.assertEqual(self.module.compare_observation(None, new)['state'], 'blocked')

if __name__ == '__main__':
    unittest.main()
