# -*- coding: utf-8 -*-
from tinySelf.vm.bytecodes import disassemble
from tinySelf.vm.bytecodes import bytecode_tokenizer
from tinySelf.vm.bytecodes import bytecode_detokenizer
from tinySelf.vm.bytecodes import BYTECODE_NOP
from tinySelf.vm.bytecodes import BYTECODE_SEND
from tinySelf.vm.bytecodes import BYTECODE_LOCAL_SEND_UNARY
from tinySelf.vm.bytecodes import BYTECODE_LOCAL_SEND_BINARY
from tinySelf.vm.bytecodes import BYTECODE_LOCAL_SEND_KEYWORD
from tinySelf.vm.bytecodes import BYTECODE_PUSH_LITERAL
from tinySelf.vm.bytecodes import LITERAL_TYPE_STR

from tinySelf.vm.bytecodes import SEND_TYPE_UNARY
from tinySelf.vm.bytecodes import SEND_TYPE_BINARY
from tinySelf.vm.bytecodes import SEND_TYPE_UNARY_RESEND
from tinySelf.vm.bytecodes import SEND_TYPE_KEYWORD_RESEND


def dynamic_recompiler(program_counter, code_context, obj):
    bytecode_tokens = []

    for token in bytecode_tokenizer(code_context.bytecodes):
        if not bytecode_tokens:
            bytecode_tokens.append(token)
            continue

        token_index = token[0]
        token_type = token[1]

        if token_type != BYTECODE_SEND:
            bytecode_tokens.append(token)
            continue

        last_token = bytecode_tokens[-1]
        last_token_type = last_token[1]
        last_token_literal_type = last_token[2]

        if (last_token_type == BYTECODE_PUSH_LITERAL and
                last_token_literal_type == LITERAL_TYPE_STR and _not_resend(token)):
            literal_index = last_token[3]
            msg_box = code_context.literals[literal_index]
            msg_name = msg_box.value

            if msg_name in obj.map._slots:
                # replace BYTECODE_PUSH_LITERAL with NOPs
                push_literal = bytecode_tokens.pop()
                push_literal_index = push_literal[0]
                bytecode_tokens.append([push_literal_index, BYTECODE_NOP])
                bytecode_tokens.append([push_literal_index + 1, BYTECODE_NOP])
                bytecode_tokens.append([push_literal_index + 2, BYTECODE_NOP])

                send_type = token[2]
                number_of_parameters = token[3]

                message_index = obj.map._slots[msg_name]
                bytecode_tokens.append([
                    token_index,
                    _get_local_send_type(send_type),
                    message_index,
                    number_of_parameters,
                ])
                continue

        bytecode_tokens.append(token)

    assert len(code_context.bytecodes) == len(bytecode_detokenizer(bytecode_tokens))

    # _print_tokens(lambda: disassemble(code_context.bytecodes))
    # print("--")
    # _print_tokens(lambda: disassemble([], bytecode_tokens))

    code_context.swap_bytecodes(bytecode_detokenizer(bytecode_tokens))

    return program_counter


def _print_tokens(token_generator):
    for token in token_generator():
        print("\t%s" % token)


def _not_resend(token):
    send_type = token[2]

    if send_type == SEND_TYPE_UNARY_RESEND or send_type == SEND_TYPE_KEYWORD_RESEND:
        return False

    return True


def _get_local_send_type(send_type):
    if send_type == SEND_TYPE_UNARY:
        return BYTECODE_LOCAL_SEND_UNARY

    if send_type == SEND_TYPE_BINARY:
        return BYTECODE_LOCAL_SEND_BINARY

    return BYTECODE_LOCAL_SEND_KEYWORD
