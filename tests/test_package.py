import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

VALIDATOR = Path(__file__).resolve().parents[1] / 'scripts/validate_package.py'

class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'plugin'
        self.root.mkdir()
        self.source = {
            'id': 'court', 'name': 'Court', 'publisher': 'Court',
            'jurisdiction': 'India', 'record_types': ['judgments'],
            'url': 'https://court.gov.in/', 'legacy_urls': [],
            'official_provenance_url': 'https://court.gov.in/',
            'verification_status': 'page_inspected', 'checked_on': '2026-10-10',
            'access': {'login': 'not_observed', 'operation': 'public reading'},
            'api': {'status': 'unverified'}, 'enabled': True,
            'exclusion_reason': None, 'official': True,
        }
        for relative in ('plugin.json', '.codex-plugin/plugin.json', '.claude-plugin/plugin.json'):
            self.write(relative, {'name': 'indian-law', 'version': '0.1.0',
                'description': 'Official research', 'author': {'name': 'Project'},
                'skills': './skills/'})
        self.write('skills/indian-law/references/sources.json', {'sources': [self.source]})
        skill = self.root / 'skills/indian-law/SKILL.md'
        skill.write_text('---\nname: indian-law\ndescription: Research law.\n---\nRead [sources](references/sources.json).\n')
        spec = importlib.util.spec_from_file_location('validator', VALIDATOR)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def write(self, rel, value):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(value))

    def errors(self, sources=None):
        if sources is not None:
            self.write('skills/indian-law/references/sources.json', {'sources': sources})
        return self.module.validate_package(self.root)

    def test_valid_package(self):
        self.assertEqual(self.errors(), [])

    def test_duplicate_source_ids(self):
        self.assertTrue(self.errors([self.source, copy.deepcopy(self.source)]))

    def test_unofficial_source_cannot_be_enabled(self):
        self.source['official'] = False
        self.assertTrue(self.errors([self.source]))

    def test_unresolved_candidate_is_discoverable_not_queryable(self):
        self.source.update(url=None, verification_status='candidate_unverified')
        self.assertTrue(self.errors([self.source]))
        self.source['enabled'] = False
        self.source['exclusion_reason'] = 'Resolve official endpoint before use'
        self.assertEqual(self.errors([self.source]), [])

    def test_api_requires_contract_and_verification(self):
        self.source['api'] = {'status': 'verified_available'}
        self.assertTrue(self.errors([self.source]))

    def test_official_linked_external_host_is_valid(self):
        self.source.update(url='https://cdn.example.net/judgment.pdf',
                           official_provenance_url='https://court.gov.in/judgments/')
        self.assertEqual(self.errors([self.source]), [])

    def test_missing_provenance_rejected(self):
        self.source['official_provenance_url'] = None
        self.assertTrue(self.errors([self.source]))

    def test_manifest_path_escape_rejected(self):
        self.write('.codex-plugin/plugin.json', {'name': 'indian-law', 'version': '0.1.0',
            'description': 'Research', 'author': {'name': 'Project'}, 'skills': './../outside'})
        self.assertTrue(self.errors())

    def test_manifest_symlink_escape_rejected(self):
        outside = Path(self.tmp.name) / 'outside'
        outside.mkdir()
        (self.root / 'outside-link').symlink_to(outside, target_is_directory=True)
        self.write('.codex-plugin/plugin.json', {'name': 'indian-law', 'version': '0.1.0',
            'description': 'Research', 'author': {'name': 'Project'}, 'skills': './outside-link'})
        self.assertTrue(self.errors())

    def test_manifest_versions_must_match(self):
        self.write('.claude-plugin/plugin.json', {'name': 'indian-law', 'version': '0.2.0'})
        self.assertTrue(self.errors())

    def test_broken_reference_rejected(self):
        (self.root / 'skills/indian-law/SKILL.md').write_text(
            '---\nname: indian-law\ndescription: Law.\n---\nRead [x](references/absent.md).')
        self.assertTrue(self.errors())

    def test_invalid_json_reported_not_crashed(self):
        (self.root / 'skills/indian-law/references/sources.json').write_text('{')
        self.assertTrue(self.errors())

    def test_watchlist_unknown_source_rejected(self):
        self.write('skills/indian-law/assets/watchlist.json',
            {'id': 'watch', 'items': [{'source_ids': ['unknown']}],
             'schedule': {'mode': 'manual'}, 'notifications': {}, 'retention': {}})
        self.assertTrue(self.errors())

    def test_watchlist_timezone_required_when_scheduled(self):
        self.write('skills/indian-law/assets/watchlist.json',
            {'id': 'watch', 'items': [], 'schedule': {'mode': 'scheduled'},
             'notifications': {}, 'retention': {}})
        self.assertTrue(self.errors())

    def test_watchlist_secrets_rejected(self):
        self.write('skills/indian-law/assets/watchlist.json',
            {'id': 'watch', 'items': [], 'schedule': {'mode': 'manual'},
             'notifications': {}, 'retention': {}, 'session_cookie': 'sensitive'})
        self.assertTrue(self.errors())

    def test_malformed_manifest_identity_reported_not_crashed(self):
        self.write('.claude-plugin/plugin.json', {'name': [], 'version': {}})
        self.assertTrue(self.errors())

    def test_malformed_watch_source_id_reported_not_crashed(self):
        self.write('skills/indian-law/assets/watchlist.json',
            {'id': 'w', 'items': [{'source_ids': [{}]}], 'schedule': {'mode':'manual'}})
        self.assertTrue(self.errors())

    def test_enabled_unverified_state_rejected(self):
        for state in ['candidate_unverified', 'excluded_secondary', 'unexpected', [], {}]:
            with self.subTest(state=state):
                row = dict(self.source, verification_status=state)
                self.assertTrue(self.errors([row]))

    def test_watchlist_client_secret_rejected(self):
        self.write('skills/indian-law/assets/watchlist.json',
            {'id':'w','items':[],'schedule':{'mode':'manual'}, 'client_secret':'synthetic'})
        self.assertTrue(self.errors())

    def test_empty_sources_rejected(self):
        self.assertTrue(self.errors([]))

    def test_mcp_script_escape_rejected(self):
        self.write('.mcp.json', {'mcpServers':{'evidence':{'command':'uv','args':['run','--script','./../outside.py']}}})
        self.assertTrue(self.errors())

    def test_mcp_cwd_escape_rejected(self):
        self.write('.mcp.json', {'mcpServers':{'evidence':{'command':'uv','args':[],'cwd':'../'}}})
        self.assertTrue(self.errors())

    def test_inline_claude_mcp_requires_bundled_script(self):
        self.write('.claude-plugin/plugin.json',{'name':'indian-law','version':'0.1.0','description':'Official research','mcpServers':{'evidence':{'command':'uv','args':['run','--script','${CLAUDE_PLUGIN_ROOT}/absent.py']}}})
        self.assertTrue(self.errors())

if __name__ == '__main__':
    unittest.main()
