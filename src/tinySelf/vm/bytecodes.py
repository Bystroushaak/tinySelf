# -*- coding: utf-8 -*-

BYTECODE_SEND = 0
# BYTECODE_SELF_SEND = 1
BYTECODE_PUSH_SELF = 2
BYTECODE_PUSH_LITERAL = 3
BYTECODE_RETURN_TOP = 4
BYTECODE_RETURN_IMPLICIT = 5
BYTECODE_ADD_SLOT = 6
BYTECODE_LOCAL_SEND = 7
BYTECODE_PARENT_SEND = 8
BYTECODE_NOP = 9

LITERAL_TYPE_NIL = 0
LITERAL_TYPE_INT = 1
LITERAL_TYPE_STR = 2
LITERAL_TYPE_OBJ = 3
LITERAL_TYPE_FLOAT = 4
LITERAL_TYPE_BLOCK = 5
LITERAL_TYPE_ASSIGNMENT = 6

SEND_TYPE_UNARY = 0
SEND_TYPE_BINARY = 1
SEND_TYPE_KEYWORD = 2
SEND_TYPE_UNARY_RESEND = 3
SEND_TYPE_KEYWORD_RESEND = 4

SLOT_NORMAL = 0
SLOT_PARENT = 1


def _compute_index(bytecodes_len, bytecodes):
    return bytecodes_len - len(bytecodes)


def bytecode_tokenizer(bytecodes):
    bytecodes = [ord(c) for c in bytecodes]
    bytecodes_len = len(bytecodes)
    while bytecodes:
        index = _compute_index(bytecodes_len, bytecodes)
        bytecode = bytecodes.pop(0)

        if bytecode == BYTECODE_SEND:
            send_type = bytecodes.pop(0)
            number_of_params = bytecodes.pop(0)

            yield [index, bytecode, send_type, number_of_params]

        elif bytecode == BYTECODE_PUSH_LITERAL:
            literal_type = bytecodes.pop(0)
            literal_index = bytecodes.pop(0)

            yield [index, bytecode, literal_type, literal_index]

        elif (bytecode == BYTECODE_RETURN_TOP or
              bytecode == BYTECODE_RETURN_IMPLICIT or
              bytecode == BYTECODE_PUSH_SELF):
            yield [index, bytecode]

        elif bytecode == BYTECODE_ADD_SLOT:
            slot_type = bytecodes.pop(0)

            yield [index, bytecode, slot_type]

        else:
            yield [index, bytecode]


def disassemble(bytecodes, tokens=None):
    disassembled = []

    if not tokens:
        tokens = bytecode_tokenizer(bytecodes)

    for token in tokens:
        index = str(token[0])
        bytecode = token[1]

        if bytecode == BYTECODE_SEND:
            send_type = token[2]
            number_of_params = token[3]

            send_type_str = {
                SEND_TYPE_UNARY: "UNARY",
                SEND_TYPE_BINARY: "BINARY",
                SEND_TYPE_KEYWORD: "KEYWORD",
                SEND_TYPE_UNARY_RESEND: "UNARY_RESEND",
                SEND_TYPE_KEYWORD_RESEND: "KEYWORD_RESEND",
            }[send_type]

            disassembled.append([
                index,
                "SEND",
                "type:" + send_type_str,
                "params:" + str(number_of_params)
            ])

        elif bytecode == BYTECODE_LOCAL_SEND:
            message_index = token[2]

            disassembled.append([
                index,
                "LOCAL_SEND",
                "message_index:" + str(message_index),
            ])

        elif bytecode == BYTECODE_PUSH_SELF:
            disassembled.append([
                index,
                "PUSH_SELF"
            ])

        elif bytecode == BYTECODE_PUSH_LITERAL:
            literal_type = token[2]
            literal_index = token[3]

            literal_type_str = {
                LITERAL_TYPE_NIL: "NIL",
                LITERAL_TYPE_INT: "INT",
                LITERAL_TYPE_STR: "STR",
                LITERAL_TYPE_OBJ: "OBJ",
                LITERAL_TYPE_FLOAT: "FLOAT",
                LITERAL_TYPE_BLOCK: "BLOCK",
                LITERAL_TYPE_ASSIGNMENT: "ASSIGNMENT",
            }[literal_type]

            disassembled.append([
                index,
                "PUSH_LITERAL",
                "type:" + literal_type_str,
                "index:" + str(literal_index)
            ])

        elif bytecode == BYTECODE_RETURN_TOP:
            disassembled.append([
                index,
                "RETURN_TOP"
            ])

        elif bytecode == BYTECODE_RETURN_IMPLICIT:
            disassembled.append([
                index,
                "RETURN_IMPLICIT"
            ])

        elif bytecode == BYTECODE_ADD_SLOT:
            slot_type = token[2]
            slot_type_str = {
                SLOT_NORMAL: "SLOT_NORMAL",
                SLOT_PARENT: "SLOT_PARENT",
            }[slot_type]

            disassembled.append([
                index,
                "ADD_SLOT",
                "type:" + slot_type_str,
            ])

        elif bytecode == BYTECODE_NOP:
            disassembled.append([
                index,
                "NOP"
            ])

        else:
            disassembled.append([
                index,
                "UNKNOWN:%s" % bytecode
            ])

    return disassembled
