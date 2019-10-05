# -*- coding: utf-8 -*-
from tinySelf.shared.code_generalization import create_copy_with_different_types


class LinkedListBox(object):
    def __init__(self, value):
        self.value = value

        self._next = None
        self._prev = None


class LinkedListForObjects(object):
    def __init__(self):
        self._first_item = None
        self._last_item = None
        self.length = 0

    def __len__(self):
        return self.length

    def __getitem__(self, index):
        boxed_item = self._get_boxed_item_on_index(index)
        return boxed_item.value

    def __setitem__(self, index, value):
        boxed_item = self._get_boxed_item_on_index(index)
        boxed_item.value = value

    def _get_boxed_item_on_index(self, index):
        if self._first_item is None:
            raise IndexError("Invalid index `%s` (empty list)." % index)

        if index + 1 > self.length:
            raise IndexError("Invalid index `%s`." % index)

        if index < -1:
            raise IndexError("Negative indexes not yet supported!")

        if index == -1:
            return self._last_item
        elif index == 0:
            return self._first_item

        boxed_item = self._first_item._next
        for _ in range(index - 1):
            boxed_item = boxed_item._next

        return boxed_item

    def pop_first(self):
        if self.length == 0:
            raise IndexError("pop from empty list")
        elif self.length == 1:
            first_item_box = self._first_item

            self._first_item = None
            self._last_item = None
            self.length = 0

            return first_item_box.value

        first_item_box = self._first_item
        self._first_item = self._first_item._next
        self._first_item._prev = None
        self.length -= 1

        return first_item_box.value

    def pop_last(self):
        if self.length == 0:
            raise IndexError("pop from empty list")
        elif self.length == 1:
            self.length = 0
            last_item_box = self._last_item

            self._first_item = None
            self._last_item = None

            return last_item_box.value

        last_item_box = self._last_item
        self._last_item = self._last_item._prev
        self._last_item._next = None
        self.length -= 1

        return last_item_box.value

    def append(self, item):
        boxed_item = LinkedListBox(item)

        if self._first_item is None:
            self._first_item = boxed_item
            self._last_item = boxed_item
            self.length += 1
            return

        boxed_item._prev = self._last_item
        self._last_item._next = boxed_item
        self._last_item = boxed_item

        self.length += 1

    def to_list(self):
        if self._first_item is None:
            return []

        boxed_item = self._first_item
        items = [boxed_item.value]
        while boxed_item._next is not None:
            boxed_item = boxed_item._next
            items.append(boxed_item.value)

        return items


class TwoPointerArray(object):
    def __init__(self, length):
        self._allocated_length = length
        self._array = [None for _ in xrange(length)]
        self._left_pointer = 0
        self._right_pointer = 0

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


class NumericTwoPointerArray(TwoPointerArray):
    """Just placeholder for the IDE."""


exec create_copy_with_different_types(TwoPointerArray, "NumericTwoPointerArray",
                                      [["None", "0"]])
