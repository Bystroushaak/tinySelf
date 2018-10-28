# -*- coding: utf-8 -*-
from pytest import raises

from tinySelf.vm.interpreter import NIL
from tinySelf.vm.interpreter import Interpreter

from tinySelf.vm.code_context import CodeContext

from tinySelf.vm.primitives import get_primitives
from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.primitives import PrimitiveStrObject

from tinySelf.parser import lex_and_parse


def test_interpreter():
    ast = lex_and_parse("""(|
        a <- 1.
        add: b = (||
            (a + 1) + b
        )
    |) add: 2""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(context, universe=get_primitives())

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
    interpreter = Interpreter(context, universe=get_primitives())

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
    interpreter = Interpreter(context, universe=get_primitives())

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
    interpreter = Interpreter(context, universe=get_primitives())

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
    interpreter = Interpreter(context, universe=get_primitives())

    interpreter.interpret()
    assert interpreter.process.result == PrimitiveIntObject(7)


def test_resend():
    ast = lex_and_parse("""(|
        p* = (| xex = 1. |).
        q* = (| xex = 2. |).

        fetchXex = (|| q.xex)
    |) fetchXex""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(context, universe=get_primitives())

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
    interpreter = Interpreter(context, universe=get_primitives())

    interpreter.interpret()
    assert interpreter.process.result == PrimitiveIntObject(2)


def test_resend_keyword():
    ast = lex_and_parse("""(|
        p* = (| xex: a = (|| 1). |).
        q* = (| xex: a = (|| a). |).

        fetchXex = (|| q.xex: 2)
    |) fetchXex""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(context, universe=get_primitives())

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

    interpreter = Interpreter(None, universe=get_primitives())
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
    interpreter = Interpreter(context, universe=get_primitives())

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
    interpreter = Interpreter(context, universe=get_primitives())

    interpreter.interpret()


def test_unhandled_error():
    ast = lex_and_parse("""(|
        test = (||
            primitives interpreter error: 'Test'
        )
    |) test""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(context, universe=get_primitives())

    interpreter.interpret()
    assert interpreter.process.finished
    assert interpreter.process.finished_with_error
    assert interpreter.process.result == PrimitiveStrObject("Test")


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
    interpreter = Interpreter(context, universe=get_primitives())

    interpreter.interpret()
    assert interpreter.process.finished
    assert not interpreter.process.finished_with_error
    result = interpreter.process.result
    assert result == PrimitiveIntObject(2)
