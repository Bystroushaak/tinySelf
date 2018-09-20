# -*- coding: utf-8 -*-
from collections import OrderedDict

from rply.token import BaseBox


class Object(object):
    def __init__(self, obj_map=None):
        if obj_map is None:
            obj_map = ObjectMap()

        self.map = obj_map
        self.slots_references = []

    @property
    def has_code(self):
        return self.map.code_context is not None

    @property
    def has_primitive_code(self):
        return self.map.primitive_code is not None

    @property
    def is_assignment_primitive(self):
        return False

    def clone(self):
        o = Object(obj_map=self.map)
        o.slots_references = self.slots_references[:]
        return o

    def set_slot(self, slot_name, value):
        slot_index = self.map.slots.get(slot_name, -1)

        if slot_index is -1:
            return False

        self.slots_references[slot_index] = value
        return True

    def get_slot(self, slot_name):
        slot_index = self.map.slots.get(slot_name, None)
        if slot_index is not None:
            return self.slots_references[slot_index]

        return None

    def get_slot_from_parents(self, slot_name):
        """
        Todo: optimize by compilation and version checking.
        """
        # TODO: rewrite this nonsense
        for parent in self.map.parent_slots:
            if slot_name in parent.map.slots:
                return parent.get_slot(slot_name)

            result = parent.get_slot_from_parents(slot_name)
            if result is None:
                continue

            return result

        return None

    # meta operations
    def meta_add_slot(self, slot_name, value):  # TODO: support auto Nil value
        assert isinstance(value, Object)

        if slot_name in self.map.slots:
            self.set_slot(slot_name, value)

        new_map = self.map.clone()
        new_map.add_slot(slot_name, len(self.slots_references))

        self.slots_references.append(value)
        self.map = new_map

    def meta_remove_slot(self, slot_name):
        if slot_name not in self.map.slots:
            return

        new_map = self.map.clone()
        slot_index = new_map.slots[slot_name]
        new_map.remove_slot(slot_name)

        self.slots_references = [
            self.slots_references[i]
            for i in range(len(self.slots_references))
            if i != slot_index
        ]

        for name, reference in new_map.slots.iteritems():
            if reference >= i:
                new_map.slots[name] -= 1

        self.map = new_map

    def meta_insert_slot(self, index, slot_name, value):  # TODO: support auto Nil value
        if slot_name in self.map.slots:
            self.set_slot(slot_name, value)

        new_map = self.map.clone()
        is_slot_inserted = new_map.insert_slot(index, slot_name)

        if is_slot_inserted:
            new_slots_references = (len(self.slots_references) + 1) * [None]
            for i in range(len(self.slots_references)):
                if i == index:
                    new_slots_references[i] = value
                elif i < index:
                    new_slots_references[i] = self.slots_references[i]
                elif i > index:
                    new_slots_references[i + 1] = self.slots_references[i]

            self.slots_references = new_slots_references
            self.map = new_map

    def meta_add_parent(self, parent_name, value):
        assert isinstance(value, Object)
        self.map.add_parent(parent_name, value)

    def meta_set_parameters(self, parameters):
        self.map.parameters = parameters

    def meta_set_ast(self, ast):
        assert isinstance(ast, BaseBox)
        self.map.ast = ast

    def meta_set_code_context(self, code_context):
        self.map.code_context = code_context


class ObjectMap(object):
    def __init__(self):
        self.parameters = []

        self.slots = OrderedDict()
        self.parent_slots = OrderedDict()
        self.scope_parent = None

        self.visited = False

        self.ast = None
        # self.bytecode = None
        self.code_context = None
        self.primitive_code = None

    def clone(self):
        new_map = ObjectMap()

        new_map.slots = self.slots.copy()
        new_map.parameters = self.parameters[:]
        new_map.parent_slots = self.parent_slots.copy()
        new_map.scope_parent = self.scope_parent
        new_map.visited = False
        new_map.ast = self.ast
        new_map.code_context = self.code_context  # TODO: deep copy / recompile
        new_map.primitive_code = self.primitive_code

        return new_map

    # meta-modifications
    def add_slot(self, slot_name, index):
        assert isinstance(index, int)

        self.slots[slot_name] = index

    def remove_slot(self, slot_name):
        if slot_name not in self.slots:
            return False

        del self.slots[slot_name]
        return True

    def insert_slot(self, slot_index, slot_name, index):
        if slot_index < 0:
            slot_index = 0

        if slot_index > len(self.slots):
            self.add_slot(slot_name, index)

        new_slots = OrderedDict()
        for cnt, key in enumerate(self.slots.keys()):
            if cnt == slot_index:
                new_slots[slot_name] = index

            new_slots[key] = self.slots[key]

        self.slots = new_slots

    def add_parent(self, parent_name, value):
        assert isinstance(value, Object)

        self.parent_slots[parent_name] = value
    
    def remove_parent(self, parent_name):
        if parent_name not in self.parent_slots:
            return

        del self.parent_slots[parent_name]
