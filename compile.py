#! /usr/bin/env python2
# -*- coding: utf-8 -*-
import os
import sys
import os.path
import argparse

import sh


def compile_project(quit_pdb, optimize, output):
    target_path = os.path.join(
        os.path.dirname(__file__),
        "src/tinySelf/target.py"
    )
    args = {
        "opt": optimize,
        "gc": "incminimark",
        "output": output,
    }

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
        if quit_pdb:
            rpython(args, target_path, _in="\n", _out=sys.stdout, _err=sys.stderr)
        else:
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
    parser.add_argument(
        "-o",
        "--optimize",
        default=1,
        metavar="LEVEL",
        type=int,
        help="Level of optimization. Default 0."
    )
    default_name = "tSelf"
    parser.add_argument(
        "-r",
        "--output",
        default=default_name,
        metavar="NAME",
        help="Name of the output file. Default %s." % default_name
    )

    args = parser.parse_args()

    try:
        compile_project(
            args.quit_pdb,
            args.optimize,
            args.output,
        )
    except Exception as e:
        sys.stderr.write(e.message + "\n")
        sys.exit(1)
