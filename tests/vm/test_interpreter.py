# -*- coding: utf-8 -*-
from pytest import raises

from tinySelf.vm.interpreter import Frame
from tinySelf.vm.interpreter import BOXED_NIL
from tinySelf.vm.interpreter import Interpreter


def test_frame():
    f = Frame()
    f.push(1)
    f.push(2)

    assert f.pop() == 2
    assert f.pop() == 1

    with raises(IndexError):
        f.pop()

    assert f.pop_or_nil() == BOXED_NIL
    f.push(1)
    assert f.pop_or_nil() == 1
    assert f.pop_or_nil() == BOXED_NIL


def test_interpreter():
    pass
