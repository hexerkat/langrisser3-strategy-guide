#!/usr/bin/env python3
"""strategy_guide_gen.py — compile the Langrisser III Strategy Guide.

Standalone (no dependency on the patch repo's tooling): it reads the patch's
script files purely as DATA to substitute live variables, and emits the guide.

The guide TEXT is hand-authored editorial source under src/*.md with canonical
names written directly; only volatile script text is a VARIABLE, kept in sync
with the translation:

    {{en:scen005:99}}    inline EN line   (one line; <$FFFC> -> space)
    {{enf:scen005:104}}  EN dialogue flow (<$FFFC>/<$FFFD> -> spaces)
    {{jp:scen005:99}}    JP balizador (the immutable anchor)
    {{jpf:scen005:104}}  JP dialogue flow

The file id is any script stem: a scenNNN D00 file, or a string table such as
fntsys10 (item names) -> {{en:fntsys10:2}} = "Longsword".

The protagonist token <$F600><$0000> renders as the canonical name "Diehärte".
A reference to a missing entry is a hard error (don't ship a broken guide).

Scripts dir: env LANG3_SCRIPTS, else the first existing known patch checkout.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List

HERE = Path(__file__).resolve().parent.parent
PROTAGONIST = "Diehärte"

# Where the patch's scripts/ live (read-only data input).
_SCRIPT_CANDIDATES = [
    os.environ.get("LANG3_SCRIPTS", ""),
    "/home/ralf/romhack/langrisser3-english/scripts",
    "/home/ralf/Jogos/emulacao/tools/langrisser3-english/scripts",
]


def _scripts_root() -> Path:
    for c in _SCRIPT_CANDIDATES:
        if c and Path(c).is_dir():
            return Path(c)
    raise SystemExit("scripts dir not found; set LANG3_SCRIPTS to the patch "
                     "repo's scripts/ directory")


# Optional 4th segment = the LITERAL JP balizador (jp/jpf only): the literal is
# rendered AND asserted equal to the live entry at that index, so a moved/edited
# entry breaks the build (slot-parity guard for the paired EN var). e.g.
#   {{jp:scen008:72:そんな事はない}}
_VAR = re.compile(
    r'\{\{\s*(en|enf|jp|jpf)\s*:\s*([A-Za-z0-9_]+)\s*:\s*(\d+)\s*(?::\s*([^}]*?)\s*)?\}\}')
_F600 = re.compile(r'<\$F600><\$0000>')
_CTRL = re.compile(r'<\$[0-9A-Fa-f]{4}>')
_COMMENT = re.compile(r'<!--.*?-->\s*', re.DOTALL)  # authoring notes, stripped from output


def parse_entries(path: Path) -> List[str]:
    """Entry raws in order. Mirrors the patch parsers: blank lines and no-code
    header lines are skipped; every remaining line is one entry (the engine's
    <$FFFC> wraps are inline, so there is exactly one entry per physical line)."""
    out: List[str] = []
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('#') and '<$' not in line:
            continue
        if (line.startswith('Langrisser') or line.startswith('Cyber')) and '<$' not in line:
            continue
        out.append(line)
    return out


def _flow(raw: str, hero: bool) -> str:
    s = _F600.sub(PROTAGONIST, raw) if hero else raw
    s = s.replace('<$FFFD>', ' ').replace('<$FFFC>', ' ')
    return re.sub(r'\s+', ' ', _CTRL.sub('', s)).strip()


_inline = _flow  # render identically (single clean line); both names kept for clarity


class _Scripts:
    def __init__(self, root: Path):
        self.root = root
        self._cache: Dict[tuple, List[str]] = {}

    def entry(self, lang: str, scen: str, idx: int) -> str:
        key = (lang, scen)
        if key not in self._cache:
            suffix = 'E' if lang == 'en' else 'J'
            sub = 'en' if lang == 'en' else 'jp'
            self._cache[key] = parse_entries(self.root / sub / f'{scen}{suffix}.txt')
        entries = self._cache[key]
        if idx < 0 or idx >= len(entries):
            raise IndexError(f"{scen}{'E' if lang == 'en' else 'J'}.txt: entry "
                             f"{idx} out of range (0..{len(entries) - 1})")
        return entries[idx]


def render_template(template: str, scripts_root: Path) -> str:
    scripts = _Scripts(scripts_root)
    template = _COMMENT.sub('', template)

    def repl(m: 're.Match') -> str:
        kind, scen, idx, literal = m.group(1), m.group(2), int(m.group(3)), m.group(4)
        lang = 'jp' if kind.startswith('jp') else 'en'
        raw = scripts.entry(lang, scen, idx)
        rendered = _flow(raw, hero=(lang == 'en'))
        if literal is not None:
            if lang != 'jp':
                raise ValueError(f"literal balizador only valid on jp/jpf: {m.group(0)}")
            if rendered != literal:
                raise AssertionError(
                    f"JP balizador mismatch at {scen}:{idx} — source literal "
                    f"{literal!r} but live entry is {rendered!r}. The entry moved "
                    f"or its JP changed; re-pair the EN var at this index.")
        return literal if literal is not None else rendered

    return _VAR.sub(repl, template)


def build_guide(manifest_path: Path, scripts_root: Path) -> str:
    """Assemble all chapters listed in the manifest into one document."""
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    parts: List[str] = []
    for ch in manifest['chapters']:
        src = (manifest_path.parent / ch['file'])
        parts.append(render_template(src.read_text(encoding='utf-8'), scripts_root))
    return "\n\n\n".join(parts).rstrip() + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('target', help="a template path/stem under src/, OR 'all' to "
                                   "build the whole guide from src/guide.json")
    ap.add_argument('-o', '--output', type=Path)
    args = ap.parse_args(argv)
    root = _scripts_root()

    if args.target == 'all':
        md = build_guide(HERE / 'src' / 'guide.json', root)
    else:
        p = Path(args.target)
        if not p.exists():
            p = HERE / 'src' / f'{args.target}.md'
        md = render_template(p.read_text(encoding='utf-8'), root)

    if args.output:
        args.output.write_text(md, encoding='utf-8')
    else:
        sys.stdout.write(md)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
