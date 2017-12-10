#! /usr/bin/env python3


from parser import parse


def test_parse_object():
    tree = parse("(asd.)")

    assert tree.symbol == "root"
    assert tree.children[0].symbol == "expression"