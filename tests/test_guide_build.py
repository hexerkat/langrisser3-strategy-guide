#!/usr/bin/env python3
"""Guard: every chapter registered in src/guide.json renders cleanly and
contributes its top-level heading to the assembled guide.

This is the per-wave green gate for the walkthrough build-out. Registering a
chapter whose file is missing, or whose template references a missing script
entry, makes the build raise (RED); authoring the chapter correctly — file
present, all live variables resolvable — turns it GREEN. No unresolved
``{{...}}`` variable may survive into the output.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))


def _manifest():
    return json.loads((HERE / 'src' / 'guide.json').read_text(encoding='utf-8'))


def _root():
    from strategy_guide_gen import _scripts_root
    return _scripts_root()


def test_every_registered_chapter_file_exists():
    for ch in _manifest()['chapters']:
        assert (HERE / 'src' / ch['file']).is_file(), ch['file']


def test_full_build_renders_clean_and_has_all_headings():
    from strategy_guide_gen import build_guide, _VAR
    md = build_guide(HERE / 'src' / 'guide.json', _root())
    # No live variable may leak unresolved into the shipped guide.
    assert not _VAR.search(md), "unresolved variable in output"
    # Every registered chapter must contribute its H1 to the assembled doc.
    for ch in _manifest()['chapters']:
        src = (HERE / 'src' / ch['file']).read_text(encoding='utf-8')
        h1 = next(l for l in src.splitlines() if l.startswith('# '))
        assert h1 in md, (ch['file'], h1)
