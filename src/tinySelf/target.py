#! /usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
from rpython.jit.codewriter.policy import JitPolicy

from parser import lex_and_parse


def main(argv):
    # print lex_and_parse("(| a | a printLine.)")
    print lex_and_parse("1")
    return 1


def target(driver, args):
    return main, None


def jitpolicy(driver):
    return JitPolicy()


def untranslated_main():
    """
    Runs main, exiting with the appropriate exit status afterwards.
    """
    import sys
    sys.exit(main(sys.argv))
