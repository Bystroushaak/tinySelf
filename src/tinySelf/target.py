#! /usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
import os
import os.path

from rply import ParsingError
from rpython.jit.codewriter.policy import JitPolicy

from r_io import writeln
from r_io import ewriteln
from r_io import stdin_readline

from parser import lex_and_parse


def run_interactive():
    while True:
        line = stdin_readline(":> ")

        if len(line) == 0 or line == "exit":
            writeln()
            return 0

        try:
            for expr in lex_and_parse(line):
                print expr.__str__()
        except ParsingError as e:
            ewriteln("Parse error.")
            if e.message:
                ewriteln(e.message)
            continue

    return 0


def run_script(path):
    print "Running script", path  # TODO: remove

    with open(path) as f:
        try:
            for expr in lex_and_parse(f.read()):
                print expr.__str__()
        except ParsingError as e:
            ewriteln("Parse error.")
            if e.message:
                ewriteln(e.message)
            return 1

    return 0


# def run_snapshot(path):
#     print "Running snapshot", path
#     return 0


def print_help(fn):
    ewriteln("Usage:")
    ewriteln("\t%s [-h] -s FN, --snapshot FN, SCRIPT_PATH" % fn)
    ewriteln("")
    # ewriteln("\t-s FN, --snapshot FN")
    # ewriteln("\t\tRun memory snapshot `FN`.")
    # ewriteln("")
    ewriteln("\t-a FN, --ast FN")
    ewriteln("\t\tShow AST of the `FN`.")
    ewriteln("")
    ewriteln("\t-h, --help")
    ewriteln("\t\tShow this help.")
    ewriteln("")
    ewriteln("\tSCRIPT_PATH")
    ewriteln("\t\tRun script `SCRIPT_PATH`.")
    ewriteln("")


def run_command(command, file):
    if not os.path.exists(file):
        ewriteln("`%s` not found!\n" % file)
        return 1

    if command in ["-a", "--ast"]:
        with open(file) as f:
            try:
                print lex_and_parse(f.read())
            except ParsingError as e:
                ewriteln("Parse error.")
                if e.message:
                    ewriteln(e.message)
                return 1
            return 0
    # elif command in ["-s", "--snapshot"]:
    #     return run_script(file)

    ewriteln("Unknown command `%s`!" % command)
    return 1


def parse_args(argv):
    if len(argv) == 1:
        return run_interactive()

    elif len(argv) == 2:
        if argv[1] in ["-h", "--help"]:
            print_help(argv[0])
            return 0
        elif not os.path.exists(argv[1]):
            ewriteln("Unrecognized option `%s`!" % argv[1])
            return 1
        else:
            return run_script(argv[1])

    elif len(argv) == 3:
        return run_command(argv[1], argv[2])

    else:
        ewriteln("Unknown arguments `%s`!" % str(argv[1:]))
        return 1

    return 0


def main(argv):
    return parse_args(argv)


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
