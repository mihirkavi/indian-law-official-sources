import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/indian-law'
LINK = re.compile(r'\]\(([^)\s]+)\)')
DOCS = ['README.md', 'CHANGELOG.md', 'CONTRIBUTING.md', 'PRIVACY.md',
        'plugins/indian-law/README.md', 'docs/installed-demo.md', 'docs/public-validation.md']


def local_targets(markdown):
    for target in LINK.findall(markdown):
        if target.startswith(('http://', 'https://', 'mailto:', '#')):
            continue
        yield target.split('#', 1)[0]


class RepositoryTests(unittest.TestCase):
    def test_documented_local_links_resolve(self):
        for name in DOCS:
            path = ROOT / name
            with self.subTest(document=name):
                self.assertTrue(path.is_file(), f'{name} is missing')
                for target in local_targets(path.read_text()):
                    self.assertTrue((path.parent / target).exists(), f'{name} links to missing {target}')

    def test_marketplaces_describe_and_resolve_plugin(self):
        for name in ('.claude-plugin/marketplace.json', '.agents/plugins/marketplace.json'):
            with self.subTest(marketplace=name):
                data = json.loads((ROOT / name).read_text())
                entry = next(p for p in data['plugins'] if p['name'] == 'indian-law')
                source = entry['source'] if isinstance(entry['source'], str) else entry['source']['path']
                self.assertTrue((ROOT / source / 'plugin.json').is_file())
        claude = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
        self.assertTrue(claude.get('description'), 'Claude marketplace needs a top-level description')

    def test_documented_version_matches_manifest(self):
        version = json.loads((PLUGIN / 'plugin.json').read_text())['version']
        self.assertIn(f'## {version} ', (ROOT / 'CHANGELOG.md').read_text())
        self.assertIn(f'version {version}', (ROOT / 'README.md').read_text())
        self.assertIn(f'Version{version}', (PLUGIN / 'README.md').read_text().replace(' ', ''))


if __name__ == '__main__':
    unittest.main()
