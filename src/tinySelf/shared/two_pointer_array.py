# -*- coding: utf-8 -*-
from rpython.rlib import jit

from tinySelf.shared.code_generalization import create_copy_with_different_types


class TwoPointerArray(object):
    def __init__(self, length):
        self._allocated_length = length
        self._array = [None for _ in xrange(length)]
        self._left_pointer = 0
        self._right_pointer = 0

    @jit.unroll_safe
    def reset(self):
        while self._left_pointer <= self._right_pointer:
            self._array[self._left_pointer] = None
            self._left_pointer += 1

        self._left_pointer = 0
        self._right_pointer = 0

        return self

    def __len__(self):
        return self._right_pointer - self._left_pointer

    def __getitem__(self, index):
        if index >= self._right_pointer:
            raise IndexError()

        return self._array[self._left_pointer + index]

    def __setitem__(self, index, value):
        self._array[index] = value

    def pop_first(self):
        if self._left_pointer == self._right_pointer:
            raise IndexError()

        rval = self._array[self._left_pointer]
        self._array[self._left_pointer] = None
        self._left_pointer += 1
        return rval

    def pop_last(self):
        if self._left_pointer == self._right_pointer:
            raise IndexError()

        rval = self._array[self._right_pointer - 1]
        self._array[self._right_pointer - 1] = None
        self._right_pointer -= 1
        return rval

    def append(self, item):
        if self._right_pointer >= self._allocated_length:
            self._array.append(item)
            self._right_pointer += 1
            self._allocated_length += 1
            return

        self._array[self._right_pointer] = item
        self._right_pointer += 1

    def to_list(self):
        return self._array[self._left_pointer: self._right_pointer]

    def __iter__(self):
        return iter(self.to_list())


class NumericTwoPointerArray(TwoPointerArray):
    """Just placeholder for the IDE."""


exec create_copy_with_different_types(TwoPointerArray, "NumericTwoPointerArray",
                                      [["None", "0"]])
