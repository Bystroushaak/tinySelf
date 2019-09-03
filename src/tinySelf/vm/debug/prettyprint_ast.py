# -*- coding: utf-8 -*-
def pretty_print_ast(source):
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

    print ">>>%s<<<" % str

    for char in substructure_chars:
        if char in str:
            return True

    return False


if __name__ == '__main__':
    source = """Send(obj=Object(slots={test_while_100: Object(slots={i: IntNumber(0), i:: AssignmentPrimitive()}, code=[Send(obj=Block(code=[Send(obj=Send(obj=Self(), msg=Message(i)), msg=BinaryMessage(name=<, parameter=IntNumber(1)))]), msg=KeywordMessage(name=whileTrue:, parameters=[Block(code=[Send(obj=Self(), msg=KeywordMessage(name=i:, parameters=[Send(obj=Send(obj=Self(), msg=Message(i)), msg=BinaryMessage(name=+, parameter=IntNumber(1)))])), Send(obj=Self(), msg=Message(false))])])), Send(obj=Send(obj=Send(obj=Self(), msg=Message(i)), msg=Message(asString)), msg=Message(printLine))]), test_another: Object(slots={x: Nil(), x:: AssignmentPrimitive(), brekeke: Nil(), brekeke:: AssignmentPrimitive()}, code=[Send(obj=Self(), msg=KeywordMessage(name=x:, parameters=[IntNumber(0)])), Send(obj='another', msg=Message(printLine)), Send(obj=Self(), msg=Message(brekeke)), Send(obj=Block(code=[Send(obj=Send(obj=Self(), msg=Message(x)), msg=BinaryMessage(name=<, parameter=IntNumber(2)))]), msg=KeywordMessage(name=whileTrue:, parameters=[Block(code=[Send(obj=Self(), msg=KeywordMessage(name=x:, parameters=[Send(obj=Send(obj=Self(), msg=Message(x)), msg=BinaryMessage(name=+, parameter=IntNumber(1)))])), Send(obj=Self(), msg=Message(nil))])])), Send(obj=Send(obj=Send(obj=Self(), msg=Message(x)), msg=Message(asString)), msg=Message(printLine))]), test_while: Object(code=[Send(obj=Self(), msg=Message(test_while_100)), Send(obj=Self(), msg=Message(test_another))])}), msg=Message(test_while))"""
    print(pretty_print_ast(source))