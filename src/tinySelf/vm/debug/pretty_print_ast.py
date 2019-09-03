# -*- coding: utf-8 -*-
def pretty_print_ast(source):
    """
    I am really sorry for bringing yet another hacked-together state machine
    parser on the world, but I really needed it and oh god, sorry.

    If this wasn't written in the rpython, I could have tried to use something
    else.
    """
    output = ""
    indentation = 0

    dont_close = False
    wrap_after_dash = False
    closing_char = {"(": ")", "[": "]", "{": "}"}
    for i, char in enumerate(source):
        next_char = source[i + 1] if i < len(source) - 1 else ""

        if char == ")" or char == "}" or char == "]":
            if not dont_close:
                output += "\n"
                indentation -= 1
                output += "  " * indentation

            dont_close = False

        # case of ), on the end of the line
        if next_char == ",":
            wrap_after_dash = True

        output += char

        if char == "," and wrap_after_dash:
            wrap_after_dash = False
            output += "\n"
            output += "  " * indentation
            output = output[:-1]

        elif char == "(" or char == "{" or char == "[":
            closed_at = source[i:].find(closing_char[char])
            structure_str = source[i + 1 : i + closed_at]

            if next_char == closing_char[char]:
                dont_close = True

            # put thigs like Message(x) to one line, instead of three
            elif structure_str and not _contains_substructures(structure_str):
                dont_close = True
            else:
                output += "\n"
                indentation += 1
                output += "  " * indentation

    return output


def _contains_substructures(str):
    substructure_chars = "({[]}),\n"

    for char in substructure_chars:
        if char in str:
            return True

    return False
