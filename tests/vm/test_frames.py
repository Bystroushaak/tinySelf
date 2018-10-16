# -*- coding: utf-8 -*-
from pytest import raises

from tinySelf.vm.frames import MethodStack
from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.interpreter import NIL


def test_method_stack():
    f = MethodStack()
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
