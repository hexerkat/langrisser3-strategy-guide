# Langrisser III (Sega Saturn) Strategy Guide

A complete strategy guide for **Langrisser III** on the Sega Saturn, written to
go with the [English translation patch](https://github.com/hexerkat/langrisser3-english).

**Read it online:** https://hexerkat.github.io/langrisser3-strategy-guide/

It covers character creation (the questions of Lushiris), classes and class
change, the heroine love-index system, every item, a walkthrough of all 36
scenarios and the five secret stages, the endings and the best-ending route, and
the secrets and cheats.

## Quotes that follow the translation

The guide text is written by hand in `src/*.md`. Every line of in-game text it
quotes (dialogue choices, item names, scenario titles) is pulled from the patch's
script files when the guide is built, so the guide always shows the same words
as the game you patched.

| In the source | In the guide |
|---|---|
| `{{en:scen005:99}}` | the English line, on one line |
| `{{enf:scen005:104}}` | an English dialogue passage |
| `{{jp:scen005:99:実は方向オンチ}}` | the Japanese line, checked against the game |
| `{{en:fntsys10:2}}` | an item name (`Longsword`) |

## Build

```bash
export LANG3_SCRIPTS=/path/to/langrisser3-english/scripts

python3 tools/strategy_guide_gen.py all -o build/langrisser3-guide.txt
python3 tools/md_to_html.py build/langrisser3-guide.txt -o build/index.html
python3 -m pytest tests/ -q
```

The online page is built by `.github/workflows/pages.yml` from the scripts of the
latest published patch, on every push and once a week.

Chapter order lives in `src/guide.json`. Sources and acknowledgements are in
`src/sources.md`.
