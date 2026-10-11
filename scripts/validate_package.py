#!/usr/bin/env python3
"""Offline package/registry validation. Does not verify website ownership or legal text."""
import argparse
import datetime
import json
from pathlib import Path
import re
from urllib.parse import urlparse

NAME = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
VERSION = re.compile(r'^\d+\.\d+\.\d+(?:-[a-z0-9.-]+)?$')
SECRET_KEYS = {'password', 'otp', 'cookie', 'cookies', 'sessioncookie', 'apikey',
               'secret', 'accesstoken', 'refreshtoken', 'authorization', 'clientsecret',
               'token', 'idtoken', 'privatekey', 'sessiontoken', 'bearertoken'}

def secret_key(key):
    return isinstance(key, str) and ''.join(c for c in key.lower() if c.isalnum()) in SECRET_KEYS

def secure_url(value):
    if not isinstance(value, str):
        return False
    p = urlparse(value)
    return p.scheme == 'https' and bool(p.hostname) and not p.username and not p.password

def contains_secret(value):
    if isinstance(value, dict):
        return any(secret_key(k) or contains_secret(v) for k, v in value.items())
    if isinstance(value, list):
        return any(contains_secret(v) for v in value)
    return False

def validate_package(root: Path) -> list:
    root = Path(root).resolve()
    errors = []
    def read_json(path):
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            if not isinstance(data, dict):
                raise ValueError('expected an object')
            return data
        except (OSError, ValueError) as exc:
            errors.append(f'{path.name}: {exc}')
            return {}
    def inside(path):
        try:
            path.resolve().relative_to(root)
            return True
        except ValueError:
            return False
    manifests = []
    for rel in ('plugin.json', '.codex-plugin/plugin.json', '.claude-plugin/plugin.json'):
        manifest = read_json(root / rel)
        manifests.append(manifest)
        if not NAME.fullmatch(str(manifest.get('name', ''))):
            errors.append(f'{rel}: invalid name')
        if not VERSION.fullmatch(str(manifest.get('version', ''))):
            errors.append(f'{rel}: invalid version')
        if not isinstance(manifest.get('description'), str) or not manifest['description'].strip():
            errors.append(f'{rel}: description required')
        if rel.startswith('.codex') and not isinstance(manifest.get('author'), dict):
            errors.append(f'{rel}: author required')
        for key in ('skills', 'mcpServers', 'apps'):
            if key not in manifest:
                continue
            if key=='mcpServers' and isinstance(manifest[key],dict):
                continue  # Claude inline server maps are validated below.
            paths = manifest[key] if isinstance(manifest[key], list) else [manifest[key]]
            for path in paths:
                if (not isinstance(path, str) or not path.startswith('./')
                    or '..' in Path(path).parts or not inside(root / path)
                    or not (root / path).exists()):
                    errors.append(f'{rel}: invalid {key} path: {path}')
    if len({(str(m.get('name')), str(m.get('version'))) for m in manifests}) != 1:
        errors.append('Manifest names/versions differ')
    def check_servers(data, label):
        servers=data.get('mcpServers') if isinstance(data,dict) else None
        if not isinstance(servers,dict) or not servers:
            errors.append(f'{label}: MCP server map required')
            return
        for name,server in servers.items():
            if not isinstance(name,str) or not name or not isinstance(server,dict):
                errors.append(f'{label}: invalid MCP server')
                continue
            command,args=server.get('command'),server.get('args')
            if not isinstance(command,str) or not command or not isinstance(args,list) or not all(isinstance(a,str) for a in args):
                errors.append(f'{label}: stdio command/arguments required')
                continue
            cwd=server.get('cwd','.')
            if not isinstance(cwd,str) or not inside(root/cwd):
                errors.append(f'{label}: MCP cwd escapes package')
            for arg in args:
                prefix='${CLAUDE_PLUGIN_ROOT}/'
                relative=arg[len(prefix):] if arg.startswith(prefix) else arg[2:] if arg.startswith('./') else None
                if relative is not None:
                    target=root/relative
                    if not inside(target) or not target.exists():
                        errors.append(f'{label}: missing/outside MCP resource')
            if server.get('env'):
                errors.append(f'{label}: this package must not embed environment credentials')
    for filename in ('.mcp.json','mcp.json'):
        path=root/filename
        if path.exists():
            check_servers(read_json(path),filename)
    for manifest in manifests:
        if isinstance(manifest.get('mcpServers'),dict):
            check_servers({'mcpServers':manifest['mcpServers']},'inline MCP')
    skill = root / 'skills/indian-law/SKILL.md'
    try:
        body = skill.read_text(encoding='utf-8')
        if not body.startswith('---\n') or '\nname: indian-law\n' not in body:
            errors.append('Skill frontmatter/name invalid')
    except OSError as exc:
        errors.append(str(exc))
    for extra in sorted((root / 'skills').glob('*/SKILL.md')):
        text = extra.read_text(encoding='utf-8')
        name = extra.parent.name
        if not text.startswith('---\n') or f'\nname: {name}\n' not in text or '\ndescription: ' not in text:
            errors.append(f'{name}: skill frontmatter/name invalid')
    for path in root.rglob('*.md'):
        if not inside(path):
            errors.append(f'External symlink: {path.name}')
            continue
        for link in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            link = link.strip('<>').split('#')[0]
            if not link or '://' in link:
                continue
            target = path.parent / link
            if not inside(target) or not target.exists():
                errors.append(f'{path.name}: broken/outside reference {link}')
    registry = read_json(root / 'skills/indian-law/references/sources.json')
    sources = registry.get('sources', [])
    if not isinstance(sources, list) or not sources:
        errors.append('Registry must have a non-empty sources array')
        sources = []
    seen = {}
    for source in sources:
        if not isinstance(source, dict):
            errors.append('Source must be an object')
            continue
        sid = source.get('id')
        if not isinstance(sid, str) or not NAME.fullmatch(sid):
            errors.append('Invalid source id')
            continue
        if sid in seen:
            errors.append(f'{sid}: duplicate id')
        seen[sid] = source
        for key in ('name', 'publisher', 'jurisdiction', 'record_types', 'legacy_urls',
                    'verification_status', 'checked_on', 'access', 'api', 'enabled', 'official'):
            if key not in source:
                errors.append(f'{sid}: missing {key}')
        if not isinstance(source.get('enabled'), bool) or not isinstance(source.get('official'), bool):
            errors.append(f'{sid}: boolean flags required')
        status = source.get('verification_status')
        accepted = {'page_inspected', 'directory_linked', 'official_index_found'}
        if not isinstance(status, str) or status not in accepted | {'candidate_unverified', 'excluded_secondary'}:
            errors.append(f'{sid}: invalid verification status')
        if source.get('enabled'):
            if not isinstance(status, str) or status not in accepted:
                errors.append(f'{sid}: enabled source must have verified discovery provenance')
            if not source.get('official'):
                errors.append(f'{sid}: unofficial enabled source')
            if not secure_url(source.get('url')):
                errors.append(f'{sid}: resolved HTTPS endpoint required')
            if not secure_url(source.get('official_provenance_url')):
                errors.append(f'{sid}: official provenance URL required')
        elif not source.get('exclusion_reason'):
            errors.append(f'{sid}: disabled source requires a reason')
        try:
            datetime.date.fromisoformat(source.get('checked_on', ''))
        except (TypeError, ValueError):
            errors.append(f'{sid}: invalid checked_on')
        access = source.get('access', {})
        api = source.get('api', {})
        if not isinstance(access, dict) or access.get('login') not in {'not_observed', 'required_for_operation', 'unknown'}:
            errors.append(f'{sid}: invalid login assessment')
        if not isinstance(api, dict):
            errors.append(f'{sid}: API assessment must be an object')
            continue
        if api.get('status') not in {'verified_available', 'documented_restricted', 'candidate_unverified', 'unverified'}:
            errors.append(f'{sid}: invalid API assessment')
        if api.get('status') == 'verified_available':
            if not (secure_url(api.get('documentation_url')) and api.get('test_date')
                    and api.get('operations') and api.get('verification_evidence')
                    and api.get('eligibility') and api.get('auth_method')):
                errors.append(f'{sid}: verified API requires documentation, eligibility, contract and test evidence')
    watch = root / 'skills/indian-law/assets/watchlist.json'
    if watch.exists():
        data = read_json(watch)
        if contains_secret(data):
            errors.append('Watchlist must not contain credentials or session secrets')
        schedule = data.get('schedule', {})
        if not isinstance(schedule, dict) or schedule.get('mode') not in {'manual', 'scheduled'}:
            errors.append('Watchlist schedule mode invalid')
        elif schedule['mode'] == 'scheduled' and not schedule.get('timezone'):
            errors.append('Scheduled watchlist requires timezone')
        items = data.get('items', [])
        if not isinstance(items, list):
            errors.append('Watchlist items must be an array')
            items = []
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get('source_ids'), list):
                errors.append('Watchlist item must declare source_ids')
                continue
            for sid in item['source_ids']:
                if not isinstance(sid, str) or sid not in seen or not seen[sid].get('enabled'):
                    errors.append(f'Watchlist source unavailable: {sid}')
    return errors

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    findings = validate_package(args.root)
    for finding in findings:
        print(f'ERROR: {finding}')
    if not findings:
        print('Package validation passed (offline structure only).')
    raise SystemExit(bool(findings))
