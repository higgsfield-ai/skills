#!/usr/bin/env python3
"""Exercise channel script, lock and narration checks without external calls."""
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]

def load(name):
    spec = importlib.util.spec_from_file_location(name, root / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def words(n, offset):
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    return ' '.join('word' + alphabet[(i + offset) % 26] + alphabet[((i + offset) // 26) % 26] + alphabet[((i + offset) // 676) % 26]
                    for i in range(n))


def shots(offset):
    return [f'{size}: {words(3, offset + i * 10)}' for i, size in enumerate(['WIDE', 'MEDIUM', 'CU', 'DETAIL', 'ECU'])]


def main():
    validator = load('validate_motion_script')
    script = {'topic': 'Why plants grow', 'genre': 'education', 'animation_mode': 'fully_animated',
              'style': 'Paper', 'cast': [],
              'through_line': {'name': 'seed', 'asset': 'seed_prop', 'progression': 'grows', 'resolution': 'plant'},
              'arc': {'hook': 1, 'build': [], 'turn': 2, 'payoff': 3},
              'blocks': [{'n': n, 'arc_role': role,
                          'vo_line': (words(6, 0) + '. ' + words(16, 300) if n == 1 else words(22, 1000 * n)),
                          'location': location, 'through_line_state': f'stage {n}',
                          'shots': shots(n * 400), 'assets_used': [location, 'seed_prop']}
                         for n, role, location in [(1, 'hook', 'soil'), (2, 'turn', 'garden'), (3, 'payoff', 'greenhouse')]],
              'sources': ['https://example.com/plants']}
    result = validator._validate(script, 30)
    assert result['valid'], result
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'script.json'
        path.write_text(json.dumps(script))
        command = ['python3', str(root / 'validate_motion_script.py'), '--script', str(path), '--duration-seconds', '30']
        assert subprocess.run(command, capture_output=True).returncode == 0
        assert (path.parent / 'script.lock').is_file()
        assert subprocess.run(['python3', str(root / 'validate_motion_script.py'), '--script', str(path),
                               '--duration-seconds', '10', '--verify-lock'], capture_output=True).returncode != 0
        changed = json.loads(path.read_text())
        changed['blocks'][1]['vo_line'] += ' changed'
        path.write_text(json.dumps(changed))
        assert subprocess.run(command + ['--verify-lock'], capture_output=True).returncode != 0
    digest = validator._narration_digest(script)
    script['blocks'][1]['vo_line'] += ' changed'
    assert validator._narration_digest(script) != digest
    script['blocks'][1]['assets_used'] = ['garden']
    assert not validator._validate(script, 30)['valid']
    print('channel script validation, narration lock and missing-asset gate passed')


if __name__ == '__main__':
    main()
