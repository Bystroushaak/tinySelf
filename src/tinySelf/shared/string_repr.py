# -*- coding: utf-8 -*-


def unescape_esc_seq(inp):
    if len(inp) < 2:
        return inp

    out = ""
    last = inp[0]
    inp = inp[1:] + "-"

    escape = last == "\\"
    for c in inp:
        if escape:
            if c == "n":
                last = "\n"
            elif c == "t":
                last = "\t"
            else:
                last = c

        out += last

        last = "" if escape else c
        escape = not escape if c == "\\" else False

    return out


def escape(inp):
    out = ""

    for c in inp:
        if c == "\n":
            out += "\\n"
        elif c == "\t":
            out += "\\t"
        elif c == "\"":
            out += "\\\""
        elif c == "'":
            out += "\\'"
        else:
            out += c

    return out
