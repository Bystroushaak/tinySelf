#! /usr/bin/env python2
# -*- coding: utf-8 -*-
import os
import sys
import os.path
import argparse

import sh


def compile_project(quit_pdb, optimize, jit, debug, output):
    target_path = os.path.join(
        os.path.dirname(__file__),
        "src/target.py"
    )
    args = {
        "opt": optimize,
        "gc": "incminimark",
        "output": output,
    }

    if jit:
        args["translation-jit"] = True
        # args["translation-jit_profiler"] = True

    if debug:
        args["lldebug"] = True
        args["lldebug0"] = True

    if quit_pdb:
        args["batch"] = True

    rpython_path = "rpython"
    if "RPYTHON_PATH" in os.environ:
        rpython_path = os.path.join(
            os.environ["RPYTHON_PATH"],
            "rpython"
        )

    try:
        rpython = sh.Command(rpython_path)
    except sh.CommandNotFound:
        raise ValueError(
            "rpython not found!\n\nPut it into $PATH or use $RPYTHON_PATH env "
            "variable to specify it."
        )

    try:
        rpython(args, target_path, _fg=True)
    except sh.ErrorReturnCode_1:
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-q",
        "--quit-pdb",
        action="store_true",
        help=(
            "Jump out of the PDB shell in case there was an error in "
            "compilation."
        )
    )
    default_level = 1
    parser.add_argument(
        "-o",
        "--optimize",
        default=default_level,
        metavar="LEVEL",
        type=int,
        help="Level of optimization. Default %d." % default_level
    )
    default_name = "tSelf"
    parser.add_argument(
        "-r",
        "--output",
        default=default_name,
        metavar="NAME",
        help="Name of the output file. Default %s." % default_name
    )
    parser.add_argument(
        "-j",
        "--jit",
        action="store_true",
        help="Add support for JIT. Warning: really, slow compilation."
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Add debug informations into the binary."
    )

    args = parser.parse_args()

    try:
        compile_project(
            args.quit_pdb,
            args.optimize,
            args.jit,
            args.debug,
            args.output,
        )
    except Exception as e:
        sys.stderr.write(e.message + "\n")
        sys.exit(1)
