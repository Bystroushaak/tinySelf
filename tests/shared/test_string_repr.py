# -*- coding: utf-8 -*-
from tinySelf.shared.string_repr import escape
from tinySelf.shared.string_repr import unescape_esc_seq


def test_unescape_esc_seq():
    assert unescape_esc_seq(r"bleh") == "bleh"
    assert unescape_esc_seq(r"\n") == "\n"
    assert unescape_esc_seq(r"\t") == "\t"
    assert unescape_esc_seq(r"\'") == "'"
    assert unescape_esc_seq(r'\"') == '"'


def test_escape():
    assert escape('\n') == "\\n"
    assert escape('\t') == "\\t"
    assert escape('') == ""
    assert escape('asdas " asdasd') == "asdas \\\" asdasd"