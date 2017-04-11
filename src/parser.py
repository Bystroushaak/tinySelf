#! /usr/bin/env python2
# -*- coding: utf-8 -*-
#
# https://rpython.readthedocs.io/en/latest/rlib.html#ebnf
# 
from rpython.rlib.parsing.ebnfparse import parse_ebnf
from rpython.rlib.parsing.ebnfparse import make_parse_function


regexs, rules, transformer = parse_ebnf("""
IGNORE: " ";

object: ["("] slots? expressions* [")"];

expressions: (<send> ["."])* <send> ["."]?;
stuff: IDENTIFIER | value | object;

send: receiver? keyword | receiver? message;
receiver: IDENTIFIER;
message: IDENTIFIER;
keyword: FIRST_KW_IDENTIFIER >stuff< (KEYWORD_IDENTIFIER >stuff<)*;

slots: ["|"] (IDENTIFIER ["."])* ["|"];

value: <string> | <float> | <integer>;

comment: "\#.*\n";

float: integer "\." POSINT;

integer: "\-" POSINT | POSINT;

POSINT: "0|[1-9][0-9]*";

IDENTIFIER: "[a-zA-Z_][a-zA-Z0-9_\*]*";
FIRST_KW_IDENTIFIER: "[a-z][a-zA-Z0-9_]*:";
KEYWORD_IDENTIFIER: "[A-Z][a-zA-Z0-9_]*:";

string: SINGLE_QUOTED_STRING | DOUBLE_QUOTED_STRING;
SINGLE_QUOTED_STRING: "'[^\\\']*'";
DOUBLE_QUOTED_STRING: "\\"[^\\\\"]*\\"";
""")
# expressions: (stuff ".") | <expressions>*;


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
print transformer().transform(parse("(| asd. bsd. | asd)"))
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
# print parse("0 + 10 + 999")