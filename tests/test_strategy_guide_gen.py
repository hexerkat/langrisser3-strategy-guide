#!/usr/bin/env python3
"""Tests for the standalone guide template processor.

Detector mechanics on a synthetic scripts root (stable); plus a live check that
a string-table reference resolves against the real patch scripts.
"""

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))


def _synth_root(tmp_path):
    en = tmp_path / 'en'
    jp = tmp_path / 'jp'
    en.mkdir(exist_ok=True), jp.mkdir(exist_ok=True)
    (en / 'scen777E.txt').write_text(
        "Hero<$FFFF>\n"
        "What do you say?<$FFFE>\n"                    # idx1
        "Short<$FFFE>\n"                               # idx2
        "You said short.<$FFFC>Good call.<$FFFE>\n"    # idx3 (flow)
        "<$F600><$0000>, well done!<$FFFE>\n",         # idx4 (hero token)
        encoding='utf-8')
    (jp / 'scen777J.txt').write_text(
        "主人公<$FFFF>\n"
        "何と言う？<$FFFE>\n"
        "短い<$FFFE>\n"
        "短い方。<$FFFC>いいね。<$FFFE>\n"
        "<$F600><$0000>、よくやった！<$FFFE>\n",
        encoding='utf-8')
    return tmp_path


def _render(tmp_path, template):
    from strategy_guide_gen import render_template
    return render_template(template, scripts_root=_synth_root(tmp_path))


def test_inline_flow_and_jp(tmp_path):
    out = _render(tmp_path,
                  "# T\nGeier: {{en:scen777:1}}\n"
                  "- {{en:scen777:2}} -> {{enf:scen777:3}}\n"
                  "JP: {{jp:scen777:1}}\n")
    assert "# T" in out
    assert "Geier: What do you say?" in out
    assert "- Short -> You said short. Good call." in out
    assert "JP: 何と言う？" in out


def test_protagonist_token_is_canonical(tmp_path):
    assert "Hero line: Diehärte, well done!" in _render(
        tmp_path, "Hero line: {{en:scen777:4}}")
    assert "<$F600>" not in _render(tmp_path, "{{en:scen777:4}}")


def test_prose_untouched(tmp_path):
    assert _render(tmp_path, "Pierre and Liffany join.") == "Pierre and Liffany join."


def test_jp_balizador_literal_asserts_position(tmp_path):
    # {{jp:scen:idx:LITERAL}} renders the literal balizador AND asserts it equals
    # the live JP entry at that index. A matching literal renders; a mismatch
    # (entry moved / text drifted) is a hard error — this is the slot-parity guard
    # that lets the EN var at the same index be trusted.
    assert _render(tmp_path, "{{jp:scen777:1:何と言う？}}") == "何と言う？"
    with pytest.raises(AssertionError):
        _render(tmp_path, "{{jp:scen777:1:まちがい}}")


def test_missing_entry_errors(tmp_path):
    with pytest.raises(IndexError):
        _render(tmp_path, "{{en:scen777:99}}")


def test_live_fntsys_item_name():
    from strategy_guide_gen import render_template, _scripts_root
    out = render_template("Buy a {{en:fntsys10:2}}.", scripts_root=_scripts_root())
    assert out == "Buy a Longsword."
