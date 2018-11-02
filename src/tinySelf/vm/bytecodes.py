# -*- coding: utf-8 -*-

BYTECODE_SEND = 0
# BYTECODE_SELF_SEND = 1
BYTECODE_PUSH_SELF = 2
BYTECODE_PUSH_LITERAL = 3
BYTECODE_RETURN_TOP = 4
BYTECODE_RETURN_IMPLICIT = 5
BYTECODE_ADD_SLOT = 6

LITERAL_TYPE_NIL = 0
LITERAL_TYPE_INT = 1
LITERAL_TYPE_STR = 2
LITERAL_TYPE_OBJ = 3
LITERAL_TYPE_BLOCK = 4
LITERAL_TYPE_ASSIGNMENT = 5

SEND_TYPE_UNARY = 0
SEND_TYPE_BINARY = 1
SEND_TYPE_KEYWORD = 2
SEND_TYPE_UNARY_RESEND = 3
SEND_TYPE_KEYWORD_RESEND = 4

SLOT_NORMAL = 0
SLOT_PARENT = 1


def disassemble(bytecodes):
    disassembled = []

    while bytecodes:
        bytecode = bytecodes.pop(0)

        if bytecode == BYTECODE_SEND:
            send_type = bytecodes.pop(0)

            send_type_str = {
                SEND_TYPE_UNARY: "UNARY",
                SEND_TYPE_BINARY: "BINARY",
                SEND_TYPE_KEYWORD: "KEYWORD",
                SEND_TYPE_UNARY_RESEND: "UNARY_RESEND",
                SEND_TYPE_KEYWORD_RESEND: "KEYWORD_RESEND",
            }[send_type]

            number_of_params = bytecodes.pop(0)

            disassembled.append([
                "SEND",
                "type:" + send_type_str,
                "params:" + str(number_of_params)
            ])
            continue

        elif bytecode == BYTECODE_PUSH_SELF:
            disassembled.append(["PUSH_SELF"])
            continue

        elif bytecode == BYTECODE_PUSH_LITERAL:
            literal_type = bytecodes.pop(0)
            literal_index = bytecodes.pop(0)

            literal_type_str = {
                LITERAL_TYPE_NIL: "NIL",
                LITERAL_TYPE_INT: "INT",
                LITERAL_TYPE_STR: "STR",
                LITERAL_TYPE_OBJ: "OBJ",
                LITERAL_TYPE_BLOCK: "BLOCK",
                LITERAL_TYPE_ASSIGNMENT: "ASSIGNMENT",
            }[literal_type]

            disassembled.append([
                "PUSH_LITERAL",
                "type:" + literal_type_str,
                "index:" + str(literal_index)
            ])
            continue

        elif bytecode == BYTECODE_RETURN_TOP:
            disassembled.append(["RETURN_TOP"])
            continue

        elif bytecode == BYTECODE_RETURN_IMPLICIT:
            disassembled.append(["RETURN_IMPLICIT"])
            continue

        elif bytecode == BYTECODE_ADD_SLOT:
            slot_type = bytecodes.pop(0)
            slot_type_str = {
                SLOT_NORMAL: "SLOT_NORMAL",
                SLOT_PARENT: "SLOT_PARENT",
            }[slot_type]

            disassembled.append([
                "ADD_SLOT",
                "type:" + slot_type_str,
            ])
            continue

        # elif bytecode == BYTECODE_RETURNIMPLICIT:

    return disassembled
