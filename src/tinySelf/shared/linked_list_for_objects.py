# -*- coding: utf-8 -*-

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
