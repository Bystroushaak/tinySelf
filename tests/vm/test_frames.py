# -*- coding: utf-8 -*-
from pytest import raises
from pytest import fixture

from tinySelf.vm.frames import MethodStack
from tinySelf.vm.frames import ProcessStack
from tinySelf.vm.frames import ProcessCycler
from tinySelf.vm.code_context import CodeContext

from tinySelf.vm.code_context import CodeContext
from tinySelf.vm.object_layout import Object

from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.interpreter import NIL


@fixture
def code_context_with_literals():
    cc = CodeContext()
    cc.literals = [1, 2]

    return cc


def test_method_stack(code_context_with_literals):
    f = MethodStack(code_context_with_literals)
    f.push(PrimitiveIntObject(1))
    f.push(PrimitiveIntObject(2))

    assert f.pop() == PrimitiveIntObject(2)
    assert f.pop() == PrimitiveIntObject(1)

    with raises(IndexError):
        f.pop()

    assert f.pop_or_nil() == NIL
    f.push(PrimitiveIntObject(1))
    assert f.pop_or_nil() == PrimitiveIntObject(1)
    assert f.pop_or_nil() == NIL


def test_process_stack(code_context_with_literals):
    ps = ProcessStack(code_context_with_literals)

    assert not ps.is_nested_call()
    assert ps.frame is ps.top_frame()

    ps.pop_frame()
    assert ps.frame

    ps.pop_frame_down()
    assert ps.frame

    ps.pop_down_and_cleanup_frame()
    assert ps.frame


def test_process_stack_push_frame_behavior(code_context_with_literals):
    ps = ProcessStack(code_context_with_literals)
    ps.frame.push(PrimitiveIntObject(1))

    assert not ps.is_nested_call()

    cc = CodeContext()
    method = Object()
    ps.push_frame(cc, method)

    assert ps.is_nested_call()
    assert ps.frame.code_context == cc

    retval = Object()
    ps.frame.push(retval)

    assert ps._length == 2
    assert ps.frame._stack[ps.frame._length - 1] == retval
    assert ps.frame.prev_stack._stack[ps.frame.prev_stack._length - 1] != retval

    ps.pop_down_and_cleanup_frame()
    assert ps._length == 1
    assert ps.frame._stack[ps.frame._length - 1] == retval
    assert ps.frame.prev_stack is None


def test_process_cycler():
    c1 = CodeContext()
    pc = ProcessCycler(c1)

    assert pc.has_processes_to_run()

    pc.next_process()
    assert pc.process.frame.code_context is c1

    pc.next_process()
    assert pc.process.frame.code_context is c1


def test_process_cycler_multiple_processes():
    c1 = CodeContext()
    c2 = CodeContext()
    pc = ProcessCycler()

    assert not pc.has_processes_to_run()

    pc.add_process(c1)
    pc.add_process(c2)

    assert pc.has_processes_to_run()

    assert pc.process.frame.code_context is c1
    pc.next_process()
    assert pc.process.frame.code_context is c1
    pc.next_process()
    assert pc.process.frame.code_context is c2
    pc.next_process()
    assert pc.process.frame.code_context is c1
    pc.next_process()
    assert pc.process.frame.code_context is c2


def test_process_cycler_multiple_processes_remove_process():
    c1 = CodeContext()
    c2 = CodeContext()
    pc = ProcessCycler()

    pc.add_process(c1)
    pc.add_process(c2)

    assert pc.process.frame.code_context is c1
    pc.next_process()
    assert pc.process.frame.code_context is c1
    pc.next_process()
    assert pc.process.frame.code_context is c2
    pc.next_process()
    assert pc.process.frame.code_context is c1
    pc.next_process()
    assert pc.process.frame.code_context is c2

    pc.remove_active_process()

    assert pc.process.frame.code_context is c1
