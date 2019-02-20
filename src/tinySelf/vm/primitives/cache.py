# -*- coding: utf-8 -*-
"""
Cache object used in some primitives (int, float, str, ..) to hold value of map
and slots, so it is not created again and again.

For example, it doesn't really make any sense to create new maps for ints,
and it also doesn't really make any sense to .clone() them, because their
.value property is immutable.
"""


class ObjCache(object):
    def __init__(self):
        self.map = None
        self.slots = None

    def store(self, obj):
        self.map = obj.map
        self.slots = obj._slot_values
