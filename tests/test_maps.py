#!/usr/bin/env python3
"""Guard: every chapter with a battle map shows it, and the image is in the repo.

Red state (2026-10-18): the guide had no maps; tools/extract_maps.py draws them
from the Japanese disc into maps/, and the Pages build publishes that folder.
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))


def test_each_mapped_chapter_shows_its_map():
    from extract_maps import CHAPTER_MAPS
    for chapter in CHAPTER_MAPS:
        image = HERE / 'maps' / f'{chapter}.webp'
        assert image.is_file(), image
        src = (HERE / 'src' / f'{chapter}.md').read_text(encoding='utf-8')
        assert re.search(rf'^!\[[^\]]+\]\(maps/{chapter}\.webp\)$', src, re.M), chapter


def test_the_figure_reaches_the_html():
    from md_to_html import convert
    html = convert('# T\n\n![Battle map](maps/sc01.webp)\n', 'T')
    assert '<img src="maps/sc01.webp"' in html
