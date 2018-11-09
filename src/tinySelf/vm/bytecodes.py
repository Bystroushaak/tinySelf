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


def _compute_index(bytecodes_len, bytecodes):
    return bytecodes_len - len(bytecodes) - 3  # FIX later


def disassemble(bytecodes_bytearray):
    disassembled = []

    bytecodes = [ord(c) for c in bytecodes_bytearray]
    bytecodes_len = len(bytecodes)
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
                _compute_index(bytecodes_len, bytecodes),
                "SEND",
                "type:" + send_type_str,
                "params:" + str(number_of_params)
            ])
            continue

        elif bytecode == BYTECODE_PUSH_SELF:
            disassembled.append([
                _compute_index(bytecodes_len, bytecodes),
                "PUSH_SELF"
            ])
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
                _compute_index(bytecodes_len, bytecodes),
                "PUSH_LITERAL",
                "type:" + literal_type_str,
                "index:" + str(literal_index)
            ])
            continue

        elif bytecode == BYTECODE_RETURN_TOP:
            disassembled.append([
                _compute_index(bytecodes_len, bytecodes),
                "RETURN_TOP"
            ])
            continue

        elif bytecode == BYTECODE_RETURN_IMPLICIT:
            disassembled.append([
                _compute_index(bytecodes_len, bytecodes),
                "RETURN_IMPLICIT"
            ])
            continue

        elif bytecode == BYTECODE_ADD_SLOT:
            slot_type = bytecodes.pop(0)
            slot_type_str = {
                SLOT_NORMAL: "SLOT_NORMAL",
                SLOT_PARENT: "SLOT_PARENT",
            }[slot_type]

            disassembled.append([
                _compute_index(bytecodes_len, bytecodes),
                "ADD_SLOT",
                "type:" + slot_type_str,
            ])
            continue

    return disassembled
