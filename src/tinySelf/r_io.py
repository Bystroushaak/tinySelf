# -*- coding: utf-8 -*-
import os


def write(msg):
    os.write(1, msg or "")


def writeln(msg=""):
    os.write(1, msg or "")
    os.write(1, "\n")


def ewrite(msg):
    os.write(2, msg or "")


def ewriteln(msg=""):
    os.write(2, msg or "")
    os.write(2, "\n")


def stdin_readline(prompt=""):
    if prompt:
        write(prompt)

    line = os.read(0, 65535)
    assert isinstance(line, str)

    return line
