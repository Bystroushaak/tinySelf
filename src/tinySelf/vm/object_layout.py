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
        slot_index = self.map.slots.get(slot_name, None)

        if slot_index is None:
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
        for parent in self.map.parents:
            if slot_name in parent.map.slots:
                return parent.get_slot(slot_name)

            result = parent.get_slot_from_parents(slot_name)
            if result is None:
                continue

            return result

        return None

    # meta operations
    def meta_add_slot(self, slot_name, value):  # TODO: support auto Nil value
        if slot_name in self.map.slots:
            return self.set_slot(slot_name, value)

        new_map = self.map.clone()
        is_slot_added = new_map.add_slot(slot_name, len(self.slots_references))

        if is_slot_added:
            self.slots_references.append(value)
            self.map = new_map

        return is_slot_added

    def meta_remove_slot(self, slot_name):
        if slot_name not in self.map.slots:
            return False

        new_map = self.map.clone()
        slot_index = new_map.slots[slot_name]
        is_slot_removed = new_map.remove_slot(slot_name)

        if is_slot_removed:
            new_slot_references = [
                self.slots_references[i]
                for i in range(len(self.slots_references))
                if i != slot_index
            ]
            self.slots_references = new_slot_references
            self.map = new_map

        return is_slot_removed

    def meta_insert_slot(self, index, slot_name, value):  # TODO: support auto Nil value
        if slot_name in self.map.slots:
            return False

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

        return is_slot_inserted

    def meta_add_parent(self, parent_name, value):
        self.map.parent_slots[parent_name] = value
        return True

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
        new_map.ast = self.ast
        new_map.code_context = self.code_context  # TODO: deep copy / recompile
        new_map.primitive_code = self.primitive_code

        return new_map

    # meta-modifications
    def add_slot(self, slot_name, index):
        self.slots[slot_name] = index

        return True

    def delete_slot(self, slot_name):
        if not slot_name in self.slots:
            return False

        del self.slots[slot_name]
        return True

    def insert_slot(self, slot_name, index):
        new_slots = {}
        for cnt, key in enumerate(self.slots.keys()):
            if cnt == index:
                new_slots[slot_name] = index

            new_slots[key] = self.slots[key]

        return True
