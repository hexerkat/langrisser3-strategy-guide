# Langrisser III (Saturn) — Strategy Guide

A GameFAQs-style strategy guide for **Langrisser III** (Sega Saturn), built to
travel with the English translation patch
([langrisser3-english](https://github.com/)).

This repo is the **guide project** (editorial source + generator). The patch repo
ships only the **compiled result** (the guide `.txt`).

## How it works

The guide text is hand-authored editorial markdown under `src/*.md`, with
**canonical names written directly**. Only volatile in-game text is a
**variable** that the generator substitutes LIVE from the patch's script files,
so the guide always matches the current translation:

| Variable | Renders |
|---|---|
| `{{en:scen005:99}}` | the live EN line (inline) |
| `{{enf:scen005:104}}` | EN dialogue passage (joined) |
| `{{jp:scen005:99}}` | the JP balizador (immutable anchor) |
| `{{en:fntsys10:2}}` | a canonical item name (`Longsword`) |

`<$F600>` (the protagonist token) renders as **Diehärte**. A reference to a
missing entry is a hard error.

## Build

```bash
# point at the patch repo's scripts/ (or set LANG3_SCRIPTS)
export LANG3_SCRIPTS=/path/to/langrisser3-english/scripts

python3 tools/strategy_guide_gen.py all -o build/langrisser3-guide.txt   # full guide
python3 tools/strategy_guide_gen.py 01-character-creation                # one chapter -> stdout
python3 -m pytest tests/ -q                                              # tests
```

Chapter order lives in `src/guide.json`.

## Status

- ✅ Character Creation (Lushiris quiz, Q1–Q27)
- ✅ Classes & Class Change
- ✅ Heroine (love-index) system
- 🟡 Item List — Weapons done; armor / accessories / consumables / Runes to add
- ✅ Scenario 04 (walkthrough format example)
- ⬜ Walkthrough for the remaining scenarios + secret stages, endings
- ⬜ GameFAQs plain-text styling pass + final `.txt` assembly into the patch repo

## Sources

Draft sources (local, read-only): the Budianto walkthrough and the JP
`攻略データ`. They provide gameplay context only; the JP script entry is the
authoritative text. Canonical names follow the patch's `NAMES AND TERMS.txt`.
