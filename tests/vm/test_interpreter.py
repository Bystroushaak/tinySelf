# -*- coding: utf-8 -*-
import os.path

from pytest import raises

from tinySelf.parser import lex_and_parse

from tinySelf.vm.primitives import get_primitives
from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.primitives import PrimitiveStrObject

from tinySelf.vm.interpreter import Interpreter

from tinySelf.vm.code_context import CodeContext

from tinySelf.vm.virtual_machine import virtual_machine



def test_interpreter():
    ast = lex_and_parse("""(|
        a <- 1.
        add: b = (||
            (a + 1) + b
        )
    |) add: 2""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(universe=get_primitives(), code_context=context)

    interpreter.interpret()
    assert interpreter.process.result == PrimitiveIntObject(4)


def test_assignment_primitive():
    ast = lex_and_parse("""(|
        a <- 0.
        incA = (||
            a: 1.
            ^a
        )
    |) incA""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(universe=get_primitives(), code_context=context)

    interpreter.interpret()
    assert interpreter.process.result == PrimitiveIntObject(1)


def test_block():
    ast = lex_and_parse("""(|
        a <- 0.
        addTenToBlk: blk = (||
            10 + (blk value).
        ).

        add = (| tmp = 3. tmp_block. |
            tmp_block: [a + tmp].
            a: 1.  # block should reflect current scopes
            2 + addTenToBlk: tmp_block.
        )
    |) add""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(universe=get_primitives(), code_context=context)

    interpreter.interpret()
    assert interpreter.process.result == PrimitiveIntObject(16)


def test_block_with_argument():
    ast = lex_and_parse("""(|
        a <- 0.
        giveOneToBlock: blk = (||
            blk with: 1
        ).

        shouldBeThree = (| tmp = 1. block. |
            block: [| :x | a + tmp + x].
            a: 1.
            giveOneToBlock: block.
        )
    |) shouldBeThree""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(universe=get_primitives(), code_context=context)

    interpreter.interpret()
    assert interpreter.process.result == PrimitiveIntObject(3)


def test_calling_block_twice_with_argument():
    ast = lex_and_parse("""(|
        a <- 0.
        giveOneToBlock: blk = (||
            blk with: 1
        ).

        giveTwoToBlock: blk = (||
            blk with: 2
        ).

        shouldBeThree = (| tmp = 1. block. sub_result. |
            block: [| :x | a + tmp + x].
            a: 1.
            sub_result: giveOneToBlock: block.
            ^ sub_result + giveTwoToBlock: block
        )
    |) shouldBeThree""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(universe=get_primitives(), code_context=context)

    interpreter.interpret()
    assert interpreter.process.result == PrimitiveIntObject(7)


def test_resend():
    ast = lex_and_parse("""(|
        p* = (| xex = 1. |).
        q* = (| xex = 2. |).

        fetchXex = (|| q.xex)
    |) fetchXex""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(universe=get_primitives(), code_context=context)

    interpreter.interpret()
    assert interpreter.process.result == PrimitiveIntObject(2)


def test_resend_is_in_local_context():
    ast = lex_and_parse("""(|
        p* = (| xex = (|| ^1). |).
        q* = (| xex = (|| a + 1). |).
        a = 1.

        fetchXex = (|| q.xex)
    |) fetchXex""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(universe=get_primitives(), code_context=context)

    interpreter.interpret()
    assert interpreter.process.result == PrimitiveIntObject(2)


def test_resend_keyword():
    ast = lex_and_parse("""(|
        p* = (| xex: a = (|| 1). |).
        q* = (| xex: a = (|| a). |).

        fetchXex = (|| q.xex: 2)
    |) fetchXex""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(universe=get_primitives(), code_context=context)

    interpreter.interpret()
    assert interpreter.process.result == PrimitiveIntObject(2)


def test_parallelism():
    one_plus_one_ast = lex_and_parse("""(|
        add = (|| 1 + 1)
    |) add""")
    two_plus_two_ast = lex_and_parse("""(|
        add = (|| 2 + 2)
    |) add""")

    one_plus_one_ctx = one_plus_one_ast[0].compile(CodeContext())
    two_plus_two_ctx = two_plus_two_ast[0].compile(CodeContext())

    interpreter = Interpreter(universe=get_primitives())
    one_plus_one_process = interpreter.add_process(one_plus_one_ctx)
    two_plus_two_process = interpreter.add_process(two_plus_two_ctx)

    assert not one_plus_one_process.finished
    assert not one_plus_one_process.result
    assert not two_plus_two_process.finished
    assert not two_plus_two_process.result

    interpreter.interpret()

    assert one_plus_one_process.finished
    assert one_plus_one_process.result == PrimitiveIntObject(2)
    assert two_plus_two_process.finished
    assert two_plus_two_process.result == PrimitiveIntObject(4)


def test_halt():
    ast = lex_and_parse("""(|
        test = (||
            primitives interpreter halt: 'Test'
        )
    |) test""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(universe=get_primitives(), code_context=context)

    interpreter.interpret()
    assert interpreter.process.finished
    assert not interpreter.process.finished_with_error
    assert interpreter.process.result == PrimitiveStrObject("Test")


def test_setting_of_error_handler_works():
    ast = lex_and_parse("""(|
        test = (||
            primitives interpreter setErrorHandler: [:obj. :stack |
                obj printString.
            ]
        )
    |) test""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(universe=get_primitives(), code_context=context)

    interpreter.interpret()


def test_unhandled_error():
    ast = lex_and_parse("""(|
        test = (||
            primitives interpreter error: 'Test'
        )
    |) test""")

    interpreter = Interpreter(universe=get_primitives())
    process = interpreter.add_process(ast[0].compile(CodeContext()))

    interpreter.interpret()
    assert process.finished
    assert process.finished_with_error
    assert process.result == PrimitiveStrObject("Test")


def test_set_error_handler_and_handle_error():
    ast = lex_and_parse("""(|
        raiseError = (|| primitives interpreter error: 'Test'.).
        test = (||
            primitives interpreter setErrorHandler: [:msg. :err |
                primitives interpreter restoreProcess: err With: 1.
            ].
            ^ 1 + raiseError.
        )
    |) test""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(universe=get_primitives(), code_context=context)

    interpreter.interpret()
    assert interpreter.process.finished
    assert not interpreter.process.finished_with_error
    result = interpreter.process.result
    assert result == PrimitiveIntObject(2)


def test_double_return_from_block():
    source = """(|
    init_true = (| true_mirror |
        true_mirror: primitives mirrorOn: true.
        true_mirror toSlot: 'ifFalse:' Add: (| :blck | nil.).
    ).
    init_false = (| false_mirror |
        false_mirror: primitives mirrorOn: false.
        false_mirror toSlot: 'ifFalse:' Add: (| :blck | blck value.).
    ).

    test_standard_double_return: blck = (| did_run <- false. |
        [ did_run: true. ^ blck value ] value.

        did_run ifFalse: [
            primitives interpreter error: 'tsdr block did not run.'.
        ].

        primitives interpreter error: 'tsdr block did not returned.'.

        ^ 0.
    ).

    test_double_return = (| dict_mirror |
        dict_mirror: primitives mirrorOn: true.

        dict_mirror toSlot: 'run_blck:' Add: (| :blck. block_run <- false. |
            [ block_run: true. ^ blck value. ] value.

            block_run ifFalse: [
                primitives interpreter error: 'Fail block did not run.'.
            ].

            primitives interpreter error: 'Fail block did not returned.'.

            ^0.
        ).
    ).

    run = (| d |
        init_true.
        init_false.

        ((test_standard_double_return: [ 1 ]) == 1) ifFalse: [
            primitives interpreter error: 'Bad value returned from test_standard_double_return.'.
        ].

        test_double_return.

        ((true run_blck: [ 1 ]) == 1) ifFalse: [
            primitives interpreter error: 'Bad value returned from test_double_return.'.
        ].
    ).
|) run"""

    process, interpreter = virtual_machine(source, "none")

    assert process.finished
    assert not process.finished_with_error, process.result.__str__()


def test_running_self_unittest_file():
    dirname = os.path.dirname(__file__)
    source_file_path = os.path.join(dirname, "../scripts/unittest.self")
    stdlib_file_path = os.path.join(dirname, "../../objects/stdlib.tself")

    with open(source_file_path) as source_file:
        with open(stdlib_file_path) as stdlib_file:
            process, interpreter = virtual_machine(
                    source_file.read(),
                    source_file_path,
                    stdlib_file.read(),
                    stdlib_file_path
            )

    assert process.finished
    assert not process.finished_with_error, process.result.__str__()
