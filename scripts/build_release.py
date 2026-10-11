#!/usr/bin/env python3
"""Build plugin/skill ZIPs and validate the extracted plugin; no publishing."""
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile
from validate_package import validate_package

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/indian-law'
DIST = ROOT / 'dist'

def archive(source, target, prefix):
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as output:
        for path in sorted(source.rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts or path.suffix == '.pyc':
                continue
            if path.is_symlink():
                raise ValueError('Release cannot include symlinks')
            info = zipfile.ZipInfo(str(Path(prefix) / path.relative_to(source)), (2026,10,10,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100644 << 16)
            output.writestr(info, path.read_bytes())

def main():
    errors = validate_package(PLUGIN)
    if errors:
        raise ValueError(errors)
    DIST.mkdir(exist_ok=True)
    version = json.loads((PLUGIN / 'plugin.json').read_text())['version']
    if not all(part.isdigit() for part in version.split('.')) or len(version.split('.')) != 3:
        raise ValueError('Release requires a numeric semantic version')
    plugin_zip = DIST / f'indian-law-plugin-{version}.zip'
    skill_zip = DIST / f'indian-law-skill-{version}.zip'
    archive(PLUGIN, plugin_zip, 'indian-law')
    archive(PLUGIN / 'skills/indian-law', skill_zip, 'indian-law')
    apl_zip = DIST / f'quashing-application-skill-{version}.zip'
    archive(PLUGIN / 'skills/quashing-application', apl_zip, 'quashing-application')
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(plugin_zip) as zipped:
            zipped.extractall(tmp)
        errors = validate_package(Path(tmp) / 'indian-law')
        if errors:
            raise ValueError(errors)
    metadata = {'version':version, 'build_date':'2026-10-10',
                'extracted_package_validation':'passed',
                'files':[{ 'name':p.name, 'bytes':p.stat().st_size,
                           'sha256':hashlib.sha256(p.read_bytes()).hexdigest() }
                          for p in (plugin_zip, skill_zip, apl_zip)]}
    (DIST / 'release.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print(json.dumps(metadata, indent=2))

if __name__ == '__main__':
    main()
