#!/usr/bin/env python3
"""Guard: each scenario chapter is titled as the game's own title card.

Red state (2026-10-18): the table of contents had drifted from the patch's
title cards ("General Geier" vs "The Despicable General Geier", "The Wise Sage
Fauvel" vs "Sage Fauvel", "Hidden Gyudon Restaurant" vs "Forest Gyudon
Restaurant, A true story"). The cards live in the patch scripts and can change
with any translation fix, so the check reads them live. Stage ?5 has no card.
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))

_DIGITS = str.maketrans('０１２３４５６７８９？', '0123456789?')
_CHAPTER = re.compile(r'(?:Scenario|Stage) (\??\d+): (.*)')


def _cards():
    from strategy_guide_gen import _scripts_root
    cards = {}
    for f in sorted((_scripts_root() / 'en').glob('scen*E.txt')):
        for line in f.read_text(encoding='utf-8').splitlines():
            m = re.search(r'ＳＣＥＮＡＲＩＯ‐([０-９？]+)', line)
            if not m:
                continue
            body = re.sub(r'<\$[0-9A-F]{4}>', ' ', line[m.end():])
            cards.setdefault(m.group(1).translate(_DIGITS), set()).add(
                re.sub(r'[　 ]+', ' ', body).strip())
    return cards


def test_chapter_titles_are_the_title_cards():
    cards = _cards()
    manifest = json.loads((HERE / 'src' / 'guide.json').read_text(encoding='utf-8'))
    seen = 0
    for ch in manifest['chapters']:
        if not ch['file'].startswith('sc'):
            continue
        m = _CHAPTER.fullmatch(ch['title'])
        assert m, ch['title']
        num, title = m.groups()
        if num == '?5':
            continue
        assert cards.get(num) == {title}, (ch['file'], title, cards.get(num))
        h1 = next(l for l in (HERE / 'src' / ch['file']).read_text(encoding='utf-8')
                  .splitlines() if l.startswith('# '))
        assert h1 == '# ' + ch['title'], (ch['file'], h1)
        seen += 1
    assert seen == 40
