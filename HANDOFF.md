# HANDOFF — Langrisser III Strategy Guide project (2026-06-15)

Resume point for the next session. Context was cleared after this was written.

## TL;DR

The Strategy Guide is its **own repo/project** (this one). The English-patch repo
ships **only the compiled `.txt`** later. Systemic chapters are **done** and the
**Walkthrough is now complete**: all **36 scenarios + secret stages ?1–?5 +
endings/best-ending route + secrets/cheats appendix** (build = 3393 lines, suite
green, zero unresolved vars). **Next: the GameFAQs plain-text styling pass**
(79-col ASCII: TOC, anchors, dividers), then assemble the final `.txt` into the
patch repo.

### Scenario→file mapping (resolved — was the old blocker)
- **Cutscene intro** = `scen{040 + 2N}` for in-game Scenario N (Sc1→042 … Sc36→112;
  secrets ?1→114, ?2→116, ?3→118, ?4→120; ?5 = the label-less Gel bonus, no cutscene).
  Intro narration is the first paragraph after the `ＳＣＥＮＡＲＩＯ‐NN` label entry.
- **Battle file** = `scen{N+1}` (Sc1→002 … verified through Sc25→026 by location
  label + objective + roster vs Budianto). Battle-dialogue vars are NOT wired yet
  (deferred); only cutscene intro + fntsys10 item-name vars are live in the guide.

## The two repos

| | Path | Git |
|---|---|---|
| **Guide (this)** | `/home/ralf/romhack/langrisser3-strategy-guide` | `main`, pushed → **github.com/ralfguth/langrisser3-strategy-guide (PRIVATE)** |
| **Patch** | `/home/ralf/Jogos/emulacao/tools/langrisser3-english` (also worktree at `/home/ralf/romhack/langrisser3-english`) | branch `meta-guide-choice-qa`, **NOT pushed**, suite 803 green |

The patch branch keeps (these are patch QA/fixes, NOT the guide): the CHOICE-fit
detector `tools/layout_qa/choices.py`, `config/entry-annotations.json`,
`tests/test_choice_fit.py`, `tests/test_no_leading_blank_line.py`, the scen005
option fixes, and the leading-blank removal. The guide generator/templates were
removed from the patch (commit `5a73fb5`) and live here now.

## How this repo works

- Guide TEXT = hand-authored editorial markdown under `src/*.md`, **canonical
  names written directly**. Only volatile in-game text is a VARIABLE, substituted
  LIVE from the patch's scripts so the guide tracks the translation.
- Generator: `tools/strategy_guide_gen.py` (standalone — inline parser, NO
  dependency on the patch's `layout_qa`). Reads the patch `scripts/` via env
  `LANG3_SCRIPTS` (defaults to a known checkout). Strips `<!-- -->` authoring
  comments. Missing entry = hard error.
- Variables: `{{en|enf|jp|jpf:<file>:<idx>}}` where `<file>` is any script stem
  (`scen005`, `fntsys10`, …) and `<idx>` is the **parsed entry index** (0-based
  over non-blank lines; EN and JP align by index). `en`=inline, `enf`=flow
  (multi-line joined), `jp`/`jpf`=the JP balizador. `<$F600>` renders as
  **Diehärte**.
- Chapter order: `src/guide.json`.

### Build / test
```bash
export LANG3_SCRIPTS=/home/ralf/Jogos/emulacao/tools/langrisser3-english/scripts
python3 tools/strategy_guide_gen.py all -o build/langrisser3-guide.txt   # whole guide
python3 tools/strategy_guide_gen.py 04-items                             # one chapter
python3 -m pytest tests/ -q                                              # 5 tests
```

## Chapters

| File | Status |
|---|---|
| `src/01-character-creation.md` | ✅ Lushiris quiz Q1–Q27 (attribute path + bonuses) |
| `src/02-classes.md` | ✅ class lines, ladders, hidden classes, Shika/monster trees |
| `src/03-heroines.md` | ✅ love-index system, 5 heroines, shared choices, best-end cheat sheet |
| `src/04-items.md` | ✅ full item list (weapons→Runes→class-up), names = live fntsys10 vars |
| `src/sc01.md … sc36.md` | ✅ Walkthrough, all 36 scenarios (renamed `scen005.md`→`sc04.md`) |
| `src/scq1.md … scq5.md` | ✅ secret stages ?1–?5 |
| `src/endings.md` | ✅ normal vs true ending, best-ending recipe, Freya checklist, heroine choice |
| `src/cheats.md` | ✅ secrets & cheats appendix (hidden shop, scenario-select, MP bug, infinite-P, …) |

## NEXT SESSION — GameFAQs styling pass + assembly

The content is done; what remains is **presentation**:
1. **GameFAQs plain-text styling pass** — convert the assembled markdown to 79-col
   ASCII (a numbered TOC with `[xx]` anchors, section dividers, ASCII tables/boxes).
   Decide whether to extend the generator with a `--gamefaqs` text renderer or add
   a post-processor; keep the live-var substitution intact.
2. **Assemble + hand off the `.txt`** into the patch repo (the patch ships only the
   compiled result). Confirm the destination path with the user.

Authoring conventions (carry forward): per-scenario file = at-a-glance / order of
battle / buried treasure / walkthrough + `BATTLE FLOW` box / branching dialogue;
**buried-treasure item rewards are `{{en:fntsys10:N}}` vars** (track the
translation); cutscene intro is `{{enf:scen{040+2N}:idx}}`. Battle-dialogue vars
are still **deferred** — wire them per scenario using the `scen{N+1}` battle map
when desired (and run the patch CHOICE-fit detector then).

### fntsys10 item-name variables — how indices were resolved
Item names come from `fntsys10` (177 canonical entries). To get an index: parse
`scripts/jp/fntsys10J.txt`, build `{stripped_JP_name: idx}`, look up the
`攻略データ` JP name (strip `<$....>` tile codes); tile-coded / fuzzy names were
resolved manually against `fntsys10E.txt`. Reuse this for any new item refs.

## Conventions / canon (carry forward)
- **JP entry = balizador** (immutable truth). Budianto + `攻略データ` are
  context-only drafts (local, read-only); never copy their romaji names.
- Canonical names from the patch's `lang3_local_docs/NAMES AND TERMS.txt`
  (Diehärte, Liffany, Luna, Sophia, Freya, Lewin, Gilbert, Pierre, Geier,
  Emerick, Altemüller, Varna, Jugler, Fauvel, Jessica, Kirikaze, Do Kahni, Dios).
- Fractions → direct % per project canon (e.g. Star Earring "−25% MP", not ×3/4).
- **GameFAQs plain-text styling is deferred to the END** (user). Author content in
  markdown now; the final pass converts to 79-col ASCII (TOC, anchors, dividers)
  and assembles the `.txt` that goes into the patch repo.

## Source files (local, read-only)
- Budianto walkthrough: `/home/ralf/romhack/lang3_local_docs/stragegy_guide.txt`
  (per-scenario items/conditions/NPC/enemies/tactics/choices/secret triggers;
  romaji names — context only).
- JP `攻略データ`: `/home/ralf/romhack/lang3_local_docs/LANGRISSER III SS の攻略データです.txt`
  — char creation (L14–186), classes (L187–391), heroines/love-index (L393–651),
  full item list (L653–970), **buried items by scenario (L972+)**, then secret
  scenarios + endings further down (unread — start there for the walkthrough).
- Plan doc (in the patch repo, local): `archive/docs/20260614_choice_budget_and_meta_guide_plan.md`.

## Memory pointers
`project_strategy_guide_repo` (separate-repo decision), `reference_scenario_file_mapping`,
`reference_budianto_walkthrough`, `reference_names_terms_canon`,
`feedback_no_fraction_multipliers`, `feedback_structural_parity_total`.
