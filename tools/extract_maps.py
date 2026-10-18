#!/usr/bin/env python3
"""extract_maps.py: draw every battle map of the Japanese disc as an image.

The maps live in two files of the data track (decoded 2026-10-18 from the bytes,
checked by eye against every scenario):

LANG/SCEN/S00.MAP and LANG/SCEN/S00.CHR
    Both start with a table: u32 count (83), then count pairs of u32
    (first 2048-byte sector, size in bytes). Entry N of one file goes with
    entry N of the other.

A S00.MAP entry
    u32 at 0 points to a block: u32 size, u16 w1, h1 (front layer, in 8x8
    cells), u16 w2, h2 (back layer, 0 = none), then u32 offsets from the
    block start: palette A, palette B (256 colors each, 15-bit BGR), the front
    grid, the back grid, one byte of terrain per front cell.

A grid cell (u16)
    bit 15 flips the cell vertically, bit 14 horizontally, bit 12 picks
    palette B (front layer only), bits 0-11 are the cell in the S00.CHR entry
    (64 bytes, 8x8, one byte per pixel). Color 0 is transparent.

The back layer is drawn first, repeated when it is smaller than the front one,
in palette A; the front layer goes on top.

Entry N is scenario N for 1-36; the secret stages ?1-?4 are 75-78. Stage ?5
has no map of its own that could be told apart, so it gets none.

Usage:
    python3 tools/extract_maps.py --disc "/path/to/Langrisser III (Japan)" -o maps
"""
from __future__ import annotations

import argparse
import os
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent

# guide chapter -> S00.MAP entry
CHAPTER_MAPS = {f'sc{n:02d}': n for n in range(1, 37)}
CHAPTER_MAPS.update({'scq1': 75, 'scq2': 76, 'scq3': 77, 'scq4': 78})


def _toc(data: bytes) -> list:
    count = struct.unpack_from('>I', data, 0)[0]
    return [struct.unpack_from('>II', data, 4 + 8 * i) for i in range(count)]


def _entry(data: bytes, toc: list, i: int) -> bytes:
    sector, size = toc[i]
    return data[sector * 2048:sector * 2048 + size]


def _palette(b: bytes, off: int) -> list:
    out = []
    for k in range(256):
        c = struct.unpack_from('>H', b, off + 2 * k)[0] if off + 2 * k + 2 <= len(b) else 0
        out += [(c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3]
    return out


_MASK = [0, 0, 0] + [255, 255, 255] * 255


def _layer(b: bytes, grid: int, w: int, h: int, cells: bytes, pals: list):
    from PIL import Image
    img = Image.new('RGB', (w * 8, h * 8))
    mask = Image.new('L', (w * 8, h * 8))
    cache = {}
    for cy in range(h):
        for cx in range(w):
            v = struct.unpack_from('>H', b, grid + 2 * (cy * w + cx))[0]
            tile = cache.get(v)
            if tile is None:
                idx = v & 0x0FFF
                p = Image.frombytes('P', (8, 8), cells[idx * 64:idx * 64 + 64].ljust(64, b'\0'))
                if v & 0x4000:
                    p = p.transpose(Image.FLIP_LEFT_RIGHT)
                if v & 0x8000:
                    p = p.transpose(Image.FLIP_TOP_BOTTOM)
                c = p.copy()
                c.putpalette(pals[(v >> 12) & 1])
                m = p.copy()
                m.putpalette(_MASK)
                tile = cache[v] = (c.convert('RGB'), m.convert('L'))
            img.paste(tile[0], (cx * 8, cy * 8))
            mask.paste(tile[1], (cx * 8, cy * 8))
    return img, mask


def draw_map(s00_map: bytes, s00_chr: bytes, i: int):
    from PIL import Image
    b = _entry(s00_map, _toc(s00_map), i)
    cells = _entry(s00_chr, _toc(s00_chr), i)
    sub = struct.unpack_from('>I', b, 0)[0]
    size, w1, h1, w2, h2 = struct.unpack_from('>IHHHH', b, sub)
    offs, p = [], sub + 12
    while True:
        v = struct.unpack_from('>I', b, p)[0]
        if v == 0 or v > size or (offs and v <= offs[-1]):
            break
        offs.append(v)
        p += 4
    pal_a, pal_b = _palette(b, sub + offs[0]), _palette(b, sub + offs[1])
    front = _layer(b, sub + offs[2], w1, h1, cells, [pal_a, pal_b])
    out = Image.new('RGB', front[0].size, tuple(pal_a[0:3]))
    if w2 and h2:
        back = _layer(b, sub + offs[3], w2, h2, cells, [pal_a, pal_a])
        for y in range(0, out.size[1], back[0].size[1]):
            for x in range(0, out.size[0], back[0].size[0]):
                out.paste(back[0], (x, y), back[1])
    out.paste(front[0], (0, 0), front[1])
    return out


def read_disc_files(disc: Path) -> tuple:
    """S00.MAP and S00.CHR from the disc's Track 01, read with the patch's ISO tools."""
    scripts = Path(os.environ.get('LANG3_SCRIPTS', ''))
    sys.path.insert(0, str(scripts.parent / 'tools'))
    from iso_tools import build_file_index, extract_file_data
    track = sorted(disc.glob('*rack*01*.bin'))[0].read_bytes()
    index = build_file_index(track)
    get = lambda name: extract_file_data(track, index[name].extent, index[name].size)
    return get('LANG/SCEN/S00.MAP'), get('LANG/SCEN/S00.CHR')


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--disc', type=Path, default=os.environ.get('LANG3_JP_DIR'),
                    help='folder of the Japanese disc (.cue + Track .bin files)')
    ap.add_argument('-o', '--out', type=Path, default=HERE / 'maps')
    args = ap.parse_args(argv)
    s00_map, s00_chr = read_disc_files(Path(args.disc))
    args.out.mkdir(parents=True, exist_ok=True)
    for chapter, entry in CHAPTER_MAPS.items():
        path = args.out / f'{chapter}.webp'
        draw_map(s00_map, s00_chr, entry).save(path, 'WEBP', lossless=True, method=6)
        print(f'{path.name}: entry {entry}, {path.stat().st_size // 1024} KB')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
