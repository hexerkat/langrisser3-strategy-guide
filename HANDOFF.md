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

## Choice-QA rollout (SUBSTANTIALLY DONE — the guide as a translation-QA tool)

The guide's branching-dialogue tables are being rebuilt so each option is a
**JP literal balizador + live EN var + effect**, which both displays the real
in-game text and **reviews/fixes the EN translation**. Mechanism: the generator's
`{{jp:scen:idx:LITERAL}}` renders the literal AND asserts it equals the live JP
entry (slot-position guard; mismatch = build error). Format = `| JP (balizador) |
EN (in-game) | Effect |`. EN fixes (overflow past the choice budget = balloon
width − 1 cursor, OR mistranslation/unnatural vs JP) are committed to the **patch**
on `meta-guide-choice-qa`, registered in `config/entry-annotations.json`
(`class=CHOICE`) and guarded by `tests/test_choice_fit.py` + `test_entry_counts`
+ `test_control_code_parity`. See memory `feedback_guide_is_translation_qa`.

**DONE:** every cleanly-locatable love-index/persuasion block AND every
item-trigger (buried-treasure) block is wired (JP balizador + live EN) and
reviewed. **241 CHOICE entries across 41 scens** registered in
`config/entry-annotations.json`; ~35 EN choice entries fixed in the patch.
In-battle: Sc1–36 (incl. all Freya-persuasion blocks). Cutscene/inter: Sc1
(scen043), Sc7 (scen055), Sc15 (scen071), Sc16 Freya (scen072), Sc18 (scen077),
Sc19 (scen079), Sc21 truce (scen083), Sc27 (scen094), Sc29 ×2 (scen098), ?1
(scen038 ×2), ?2 Tiaris (scen039).

Sample fixes: scen018[55] わからずや "stubborn fool" (was "I don't understand");
scen018[143] "Flare"→Freya; scen033[70] まったくだ "No doubt" (was "It maybe is");
scen071[43] わかりきった "It's obvious" (was "I think I understand"); + overflow
refits (scen008/010/011/012/015/025/033/055/072/038).

**RESIDUAL — kept as effects-only tables (flagged "in-game wording pending");
no `何と` prompt found, or non-dialogue mechanism:** Sc16 present-buying
(prep-phase), Sc10 after-battle 5-option, Sc21 Emerick-near + Tiaris's-father,
Sc23 after-battle quarrel, Sc33 confession (multi-heroine). Secret-stage **trigger**
choices (scen011 ?2-trigger convos, scen035 ?4 line, scen040 Dios/Ruud) and all
**item-trigger** choices (buried-treasure selections, e.g. Love/Power/Courage,
Devil Axe, Thor blessing) are separate categories, not yet wired. To find a block:
grep `何と(答え|話しかけ|言い)` in the JP file; options follow the prompt.
To retrofit literals after writing 3-segment `{{jp:scen:idx}}` vars, re-run the
bake loop (regex `\{\{jp:(scen\w+):(\d+)\}\}` → add `:_flow(jp[idx])`).

### Item-trigger choice sweep — DONE (2026-06-15, 4 waves)

The **buried-treasure selection options** (map menu choices that grant an item —
NOT love-index) got the full QA pipeline: JP balizador + live EN var in the
*Buried treasure* table (rendered `"EN option" (JP balizador)`), EN reviewed/fixed
vs JP, registered `class=CHOICE`, choice-fit verified. Commits on the patch:
`b1e79b3` (wave A Sc3–11), `a2d3b2e` (wave B Sc14–24), `e7be892` (wave C Sc25–35),
`c5d28eb` (wave D secrets ?1–?4); guide mirrors `340d80e`/`e7ae53c`/`d410449`/`cc3437f`.

**Battle-file mapping confirmed:** in-game Sc *N* battle = `scen{N+1}` (Sc3→004 …
Sc36→037). **Secret stages live in scen038(?1)/scen039(?2)/scen040(?3)/scen041(?4)**
— NOT scen115-121 (the scq*.md header comments mislabel the battle file; the actual
choice text is in scen038-041, just before the cutscene block scen042+).

**EN fixes made (choice entries only):** overflow refits scen006[135] "It intrigues
me", scen009[60] "Reach for it", scen010[56] "Open both at once", scen018[74]
"Hiding in the back", scen019[53/55] "Dig between them"/"Stand between them",
scen023[77] "Fill your waterskin", scen041[67/68] "Press it again"/"Check its chest",
scen039[139] "Super Lang added"; mistranslations scen038[164] 放っておく "Shoot at it"
→ "Leave it alone", scen030[82] 割る "open"→"cracking", scen033[134/142] "Magic power"
→"Power of Magic" (parallel w/ 剣の力), scen033[135/143] "Despise both"→"Neither",
scen030[72] "Breath"→"Blow on it", scen040[136] "Umini"→"Uminin" (Cho Aniki canon);
menu-period normalization on the 6 scen030 options. **Biggest find: scen039[227-236]
(?2 sacrifice block) was slot-misaligned** — every EN option sat one slot above its
JP (prompt slot held option text, "Holy Beast" duplicated); rewrote each slot to
match its JP (entry count + control-code parity preserved, suite stayed green).

**Skipped (no selectable text options — yes/no or spatial, left as prose):** Sc26
NW/SE crests, Sc8/Sc31/Sc16 yes-no sub-prompts, ?3 18-or-over, ?4 safe code, and
NPC-action triggers (Dios persuades Ruud). ?5 has no items.

**RESIDUAL (still open, separate categories):** love-index blocks with no `何と`
prompt — Sc16 present-buying (prep-phase), Sc10 after-battle 5-option, Sc21
Emerick-near + Tiaris's-father, Sc23 after-battle quarrel, Sc33 confession; and
secret-stage **story-trigger** convos (scen011 ?2-trigger, scen035 ?4 line). Also a
general scen prose-polish task (NOT choice-related) is still pending — e.g. the
scen039 hero-quiz RESULT narrations have a decode bug ("lost 0P" should be "200P");
out of choice scope, flagged for that pass.

## Memory pointers
`project_strategy_guide_repo` (separate-repo decision), `reference_scenario_file_mapping`,
`reference_budianto_walkthrough`, `reference_names_terms_canon`,
`feedback_no_fraction_multipliers`, `feedback_structural_parity_total`,
`feedback_guide_is_translation_qa`, `feedback_walkthrough_scope_no_general_polish`.
