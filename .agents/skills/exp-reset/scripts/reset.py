#!/usr/bin/env python3
"""List or archive explicitly selected MVP projects. Standard library only."""
import argparse
from datetime import date, datetime, timezone
import json
from pathlib import Path
import re
import sys
import uuid

WORKBENCH = {'kind': 'exp-workbench', 'version': 2, 'backups': '.practice-backups'}
PROJECT = {'kind': 'exp-project', 'version': 1}


def marker_matches(path, expected):
    if path.is_symlink() or not path.is_file():
        return False
    try:
        return json.loads(path.read_text()) == expected
    except (ValueError, OSError):
        return False


def eligible(path):
    if path.is_symlink() or not path.is_dir():
        return False
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}-[^/\\]+', path.name):
        return False
    try:
        date.fromisoformat(path.name[:10])
    except ValueError:
        return False
    return marker_matches(path / '.exp-project.json', PROJECT)


def reset(root, projects=(), apply=False):
    root = Path(root).resolve(strict=True)
    if not marker_matches(root / '.exp-workbench.json', WORKBENCH):
        raise ValueError('Missing or unsupported workbench marker.')
    backups = root / '.practice-backups'
    if backups.is_symlink() or (backups.exists() and not backups.is_dir()):
        raise ValueError('Unexpected backup path.')
    available = sorted(p.name for p in root.iterdir() if eligible(p))
    selected = list(dict.fromkeys(projects))
    for name in selected:
        if name not in available:
            raise ValueError(f'Not an eligible project: {name}')
    if apply and not selected:
        raise ValueError('Select at least one project explicitly.')
    result = {'available': available, 'selected': selected, 'applied': False, 'backup': None}
    if not apply:
        return result
    backups.mkdir(exist_ok=True)
    batch = backups / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-') + uuid.uuid4().hex[:12])
    batch.mkdir()
    moved = []
    try:
        for name in selected:
            if not eligible(root / name):
                raise ValueError(f'Project changed since preview: {name}')
            (root / name).rename(batch / name)
            moved.append(name)
    except (OSError, ValueError):
        # Restore completed moves if a later move fails; never overwrite a new path.
        for name in reversed(moved):
            destination = root / name
            if destination.exists() or destination.is_symlink():
                raise RuntimeError(f'Recovery needed: saved project remains at {batch / name}')
            (batch / name).rename(destination)
        batch.rmdir()
        raise
    result.update(applied=True, backup=str(batch))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', action='append', default=[], help='Exact project name; repeat for multiple selections.')
    parser.add_argument('--apply', action='store_true', help='Move the selected projects into backups.')
    args = parser.parse_args()
    try:
        result = reset(Path(__file__).resolve().parents[4], args.project, args.apply)
    except (OSError, ValueError, RuntimeError) as error:
        print(f'Reset refused: {error}', file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
