#!/usr/bin/env python3
"""md_to_html.py — render the compiled guide markdown to a single self-contained
HTML file (embedded CSS, clickable TOC) for comfortable on-screen reading.

It handles exactly the markdown the guide generator emits: ATX headings, GFM
pipe tables, fenced code blocks (the ASCII battle-flow / unlock boxes), block
quotes, unordered/ordered lists, horizontal rules, and inline **bold**, *italic*,
`code`, [links](url). Japanese text is passed through (UTF-8).

Usage:
    python3 tools/md_to_html.py build/langrisser3-guide.txt -o build/langrisser3-guide.html
"""
from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from typing import List

_CODE = re.compile(r'`([^`]+)`')
_LINK = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
_BOLD = re.compile(r'\*\*(.+?)\*\*')
_ITAL = re.compile(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)')
_HR = re.compile(r'^\s*([-*_])\1{2,}\s*$')


def _slug(text: str, used: dict) -> str:
    base = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-') or 'sec'
    s = base
    n = used.get(base, 0)
    if n:
        s = f'{base}-{n}'
    used[base] = n + 1
    return s


def _inline(text: str) -> str:
    """Escape HTML, then apply inline markdown. Code spans are protected first."""
    spans: List[str] = []

    def stash(m: 're.Match') -> str:
        spans.append(f'<code>{html.escape(m.group(1))}</code>')
        return f'\x00{len(spans) - 1}\x00'

    text = _CODE.sub(stash, text)
    text = html.escape(text)
    text = _LINK.sub(lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>', text)
    text = _BOLD.sub(r'<strong>\1</strong>', text)
    text = _ITAL.sub(r'<em>\1</em>', text)
    text = re.sub(r'\x00(\d+)\x00', lambda m: spans[int(m.group(1))], text)
    return text


def _is_table_row(line: str) -> bool:
    return line.lstrip().startswith('|')


def _is_table_sep(line: str) -> bool:
    return bool(re.match(r'^\s*\|?[\s:|-]+\|[\s:|-]*$', line)) and '-' in line


def _cells(row: str) -> List[str]:
    row = row.strip()
    if row.startswith('|'):
        row = row[1:]
    if row.endswith('|'):
        row = row[:-1]
    return [c.strip() for c in row.split('|')]


def convert(md: str, title: str) -> str:
    lines = md.split('\n')
    out: List[str] = []
    toc: List[tuple] = []
    used: dict = {}
    i, n = 0, len(lines)

    while i < n:
        line = lines[i]

        # fenced code block
        if line.lstrip().startswith('```'):
            i += 1
            buf = []
            while i < n and not lines[i].lstrip().startswith('```'):
                buf.append(html.escape(lines[i]))
                i += 1
            i += 1
            out.append('<pre><code>' + '\n'.join(buf) + '</code></pre>')
            continue

        # heading
        m = re.match(r'^(#{1,6})\s+(.*)$', line)
        if m:
            level = len(m.group(1))
            txt = m.group(2).strip()
            sid = _slug(txt, used)
            if level <= 2:
                toc.append((level, sid, txt))
            out.append(f'<h{level} id="{sid}">{_inline(txt)}</h{level}>')
            i += 1
            continue

        # table
        if _is_table_row(line) and i + 1 < n and _is_table_sep(lines[i + 1]):
            header = _cells(line)
            i += 2
            body = []
            while i < n and _is_table_row(lines[i]):
                body.append(_cells(lines[i]))
                i += 1
            th = ''.join(f'<th>{_inline(c)}</th>' for c in header)
            rows = ''.join(
                '<tr>' + ''.join(f'<td>{_inline(c)}</td>' for c in r) + '</tr>'
                for r in body)
            out.append(f'<table><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table>')
            continue

        # horizontal rule
        if _HR.match(line):
            out.append('<hr>')
            i += 1
            continue

        # blockquote (consecutive > lines)
        if line.lstrip().startswith('>'):
            buf = []
            while i < n and lines[i].lstrip().startswith('>'):
                buf.append(re.sub(r'^\s*>\s?', '', lines[i]))
                i += 1
            out.append('<blockquote>' + _inline(' '.join(b for b in buf if b.strip())) + '</blockquote>')
            continue

        # lists (group consecutive items of one kind)
        if re.match(r'^\s*[-*+]\s+', line) or re.match(r'^\s*\d+\.\s+', line):
            ordered = bool(re.match(r'^\s*\d+\.\s+', line))
            tag = 'ol' if ordered else 'ul'
            items = []
            pat = r'^\s*\d+\.\s+' if ordered else r'^\s*[-*+]\s+'
            while i < n and re.match(pat, lines[i]):
                items.append(_inline(re.sub(pat, '', lines[i]).strip()))
                i += 1
            out.append(f'<{tag}>' + ''.join(f'<li>{it}</li>' for it in items) + f'</{tag}>')
            continue

        # blank line
        if not line.strip():
            i += 1
            continue

        # paragraph (gather until blank / block start)
        buf = [line]
        i += 1
        while i < n and lines[i].strip() and not re.match(r'^(#{1,6}\s|```|>|\s*[-*+]\s|\s*\d+\.\s)', lines[i]) \
                and not _is_table_row(lines[i]) and not _HR.match(lines[i]):
            buf.append(lines[i])
            i += 1
        out.append('<p>' + _inline(' '.join(buf)) + '</p>')

    toc_html = '\n'.join(
        f'<li class="lvl{lvl}"><a href="#{sid}">{html.escape(txt)}</a></li>'
        for lvl, sid, txt in toc)

    return _TEMPLATE.format(title=html.escape(title), toc=toc_html, body='\n'.join(out))


_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
:root {{ --fg:#1c1e21; --muted:#6b7280; --bg:#fbfbfa; --card:#fff; --accent:#7a1f1f;
        --border:#e3e3e0; --th:#f2efe9; --zebra:#faf8f4; --code:#f4f2ee; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg);
  font:16px/1.65 "Hiragino Kaku Gothic ProN","Noto Sans",-apple-system,Segoe UI,Roboto,sans-serif; }}
.wrap {{ max-width:60rem; margin:0 auto; padding:2rem 1.25rem 6rem; }}
h1,h2,h3,h4 {{ line-height:1.25; scroll-margin-top:1rem; }}
h1 {{ font-size:1.9rem; margin:2.6rem 0 .6rem; padding-bottom:.3rem;
  border-bottom:3px solid var(--accent); color:var(--accent); }}
h2 {{ font-size:1.3rem; margin:1.8rem 0 .5rem; color:#333; }}
h3 {{ font-size:1.08rem; margin:1.3rem 0 .4rem; }}
h4 {{ font-size:1rem; margin:1rem 0 .3rem; color:var(--muted); }}
p {{ margin:.55rem 0; }}
em {{ color:#444; }}
a {{ color:var(--accent); text-decoration:none; }}
a:hover {{ text-decoration:underline; }}
hr {{ border:0; border-top:1px solid var(--border); margin:1.6rem 0; }}
blockquote {{ margin:.8rem 0; padding:.5rem .9rem; background:var(--card);
  border-left:4px solid var(--accent); color:#333; border-radius:0 4px 4px 0; }}
table {{ border-collapse:collapse; width:100%; margin:.8rem 0; font-size:.94rem;
  background:var(--card); box-shadow:0 1px 2px rgba(0,0,0,.04); }}
th,td {{ border:1px solid var(--border); padding:.4rem .6rem; text-align:left; vertical-align:top; }}
th {{ background:var(--th); font-weight:600; }}
tbody tr:nth-child(even) {{ background:var(--zebra); }}
code {{ background:var(--code); padding:.05rem .3rem; border-radius:3px;
  font:.9em "SFMono-Regular",Consolas,"Liberation Mono",monospace; }}
pre {{ background:#1e2024; color:#e6e6e6; padding:1rem; border-radius:6px;
  overflow-x:auto; line-height:1.4; }}
pre code {{ background:none; padding:0; color:inherit;
  font:13px/1.4 "SFMono-Regular",Consolas,"Liberation Mono",monospace; white-space:pre; }}
.toc {{ background:var(--card); border:1px solid var(--border); border-radius:8px;
  padding:1rem 1.25rem; margin:1.5rem 0; columns:2; column-gap:2rem; }}
.toc h2 {{ margin:0 0 .5rem; column-span:all; }}
.toc ul {{ list-style:none; margin:0; padding:0; }}
.toc li {{ margin:.12rem 0; break-inside:avoid; }}
.toc .lvl1 a {{ font-weight:600; }}
.toc .lvl2 {{ padding-left:1rem; font-size:.92rem; }}
.toc .lvl2 a {{ color:var(--muted); }}
@media (max-width:640px) {{ .toc {{ columns:1; }} }}
</style>
</head>
<body>
<div class="wrap">
<nav class="toc"><h2>Contents</h2><ul>
{toc}
</ul></nav>
{body}
</div>
</body>
</html>
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('input', type=Path, help='compiled guide markdown (.txt/.md)')
    ap.add_argument('-o', '--output', type=Path, required=True)
    ap.add_argument('--title', default='Langrisser III — Strategy Guide')
    args = ap.parse_args(argv)
    md = args.input.read_text(encoding='utf-8')
    args.output.write_text(convert(md, args.title), encoding='utf-8')
    print(f'wrote {args.output} ({args.output.stat().st_size // 1024} KB)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
