# -*- coding: utf-8 -*-
from tinySelf.parser.ast_tokens import _escape_sequences


def test_escape_sequences():
    assert _escape_sequences(r"bleh") == "bleh"
    assert _escape_sequences(r"\n") == "\n"
    assert _escape_sequences(r"\t") == "\t"
    assert _escape_sequences(r"\'") == "'"
    assert _escape_sequences(r'\"') == '"'
