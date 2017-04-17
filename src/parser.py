#! /usr/bin/env python2
# -*- coding: utf-8 -*-
#
# https://rpython.readthedocs.io/en/latest/rlib.html#ebnf
# 
from rpython.rlib.parsing.ebnfparse import parse_ebnf
from rpython.rlib.parsing.ebnfparse import make_parse_function


regexs, rules, transformer = parse_ebnf("""
IGNORE: " |\n";

root: (expression ["\."])* expression;

object: ["("] slots? sends* [")"];
block: ["["] slots? sends* ["]"];

expression: IDENTIFIER | value | object | block | send;

sends: (send ["\."])* send ["\."]?;
send: (receiver? keyword) | (receiver? message);
receiver: IDENTIFIER | object | block;
message: IDENTIFIER;
keyword: FIRST_KW_IDENTIFIER >expression< (KEYWORD_IDENTIFIER >expression<)*;

slots: ["|"] (slot_definition ["\."])* slot_definition? ["\."]? ["|"];
slot_definition: IDENTIFIER | (FIRST_KW_IDENTIFIER >expression<) | PARAMETER;

value: <string> | <float> | <integer>;

float: integer "\." POSINT;
integer: "\-" POSINT | POSINT;

POSINT: "0|[1-9][0-9]*";

PARAMETER: ":[a-z_][a-zA-Z0-9_\*]*";
IDENTIFIER: "[a-z_][a-zA-Z0-9_\*]*";
FIRST_KW_IDENTIFIER: "[a-z_][a-zA-Z0-9_]*:";
KEYWORD_IDENTIFIER: "[A-Z][a-zA-Z0-9_]*:";

string: SINGLE_QUOTED_STRING | DOUBLE_QUOTED_STRING;
SINGLE_QUOTED_STRING: "'[^\\\']*'";
DOUBLE_QUOTED_STRING: "\\"[^\\\\"]*\\"";
""")
# expressions: (stuff "\.") | <expressions>*;


parse = make_parse_function(regexs, rules)
# parse = make_parse_function(regexs, rules, eof=True)

# print transformer().transform(parse("0"))
# print transformer().transform(parse("11"))
# print transformer().transform(parse("-23"))
# print transformer().transform(parse("1.35"))
# print transformer().transform(parse('"a"'))
# print transformer().transform(parse("'č'"))
# print transformer().transform(parse("identifier"))
# print transformer().transform(parse("IDENTIFIER"))
# print transformer().transform(parse("_identifier"))
# print transformer().transform(parse("_Identifier"))



# print transformer().transform(parse("(| asd. bsd. | 5.)"))
# print
print transformer().transform(parse("(| asd. bsd. | asd.)"))
print
print transformer().transform(parse("(| asd: 1. bsd: nil | asd.)"))
print
print transformer().transform(parse("(| asd. bsd. | asd. bsd. obj msg.)"))
print
print transformer().transform(parse("(| asd. bsd. | asd. bsd. obj msg.)"))
print
print transformer().transform(parse("(| asd. bsd. | self hello: xe.)"))
print
print transformer().transform(parse("(| asd. bsd. | self hello: xe Second: xa.)"))
print
print transformer().transform(parse("(| asd. bsd. | hello: xe.)"))
print
print transformer().transform(parse("[| asd. :bsd. | hello: xe.]"))
print "\n---\n"
print transformer().transform(parse("""

a: (| asd. bsd. | hello: xe.).

[| asd. :bsd. | hello: xe.]

"""))
# print parse("0 + 10 + 999")