# -*- coding: utf-8 -*-
from tinySelf.vm.bytecodes import disassemble
from tinySelf.vm.bytecodes import bytecode_tokenizer
from tinySelf.vm.bytecodes import BYTECODE_SEND
from tinySelf.vm.bytecodes import BYTECODE_LOCAL_SEND
from tinySelf.vm.bytecodes import BYTECODE_PUSH_LITERAL
from tinySelf.vm.bytecodes import LITERAL_TYPE_STR


def dynamic_recompiler(program_counter, code_context, obj):
    tokens = []

    for token in bytecode_tokenizer(code_context.bytecodes):
        if not tokens:
            tokens.append(token)
            continue

        token_index = token[0]
        token_type = token[1]
        last_token = tokens[-1]

        if (token_type == BYTECODE_SEND and
                last_token[1] == BYTECODE_PUSH_LITERAL and
                last_token[2] == LITERAL_TYPE_STR):
            literal_index = last_token[3]
            msg_box = code_context.literals[literal_index]
            msg_name = msg_box.value

            if msg_name in obj.map._slots:
                message_index = obj.map._slots[msg_name]
                last_token = [token_index, BYTECODE_LOCAL_SEND, message_index]
                continue

        tokens.append(token)  # prepsat z appendovani shiftnuteho tokenu na pop

    # if tokens:
    print("xexxxxxxxxxxxxxxxxxxxxxxxxxx")
    print(disassemble(code_context.bytecodes))
    print("--")
    print(disassemble([], tokens))

    return program_counter
