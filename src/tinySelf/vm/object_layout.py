# -*- coding: utf-8 -*-
from collections import OrderedDict

from rply.token import BaseBox


def unvisit(visited_objects, first_level_call):
    if not first_level_call:
        return

    for obj_map in visited_objects.keys():
        obj_map.visited = False


class _BareObject(object):
    def __init__(self, obj_map=None):
        if obj_map is None:
            obj_map = ObjectMap()

        self.map = obj_map
        self.scope_parent = None

        self._parent_slot_values = []
        self._slot_values = []

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
        o._slot_values = self._slot_values[:]
        o._parent_slot_values = self._parent_slot_values
        o.scope_parent = self.scope_parent
        self.map.used_in_multiple_objects = True

        return o

    def set_slot(self, slot_name, value):
        slot_index = self.map._slots.get(slot_name, -1)

        if slot_index is -1:
            return False

        self._slot_values[slot_index] = value
        return True

    def get_slot(self, slot_name):
        slot_index = self.map._slots.get(slot_name, -1)
        if slot_index is not -1:
            return self._slot_values[slot_index]

        return None

    def parent_lookup(self, slot_name, _visited_objects=None):
        first_level_call = False
        if _visited_objects is None:
            first_level_call = True
            # sets are not supported, see
            # https://rpython.readthedocs.io/en/latest/rpython.html
            _visited_objects = {}

        parents = []
        if self.scope_parent is not None and not self.scope_parent.visited:
            parents.append(self.scope_parent)

        parents.extend(self._parent_slot_values)

        for parent in parents:
            if parent.visited:
                continue

            parent.visited = True
            _visited_objects[parent.map] = None

            if slot_name in parent.slot_keys:
                unvisit(_visited_objects, first_level_call)
                return parent.get_slot(slot_name)

            result = parent.parent_lookup(slot_name, _visited_objects)
            if result is not None:
                unvisit(_visited_objects, first_level_call)
                return result

        unvisit(_visited_objects, first_level_call)
        return None

    def slot_lookup(self, slot_name):
        assert isinstance(slot_name, str)

        slot_index = self.map._slots.get(slot_name, -1)

        if slot_index != -1:
            return self._slot_values[slot_index]

        if self.scope_parent is not None:
            obj = self.scope_parent.get_slot(slot_name)

            if obj is not None:
                return obj

        return self.parent_lookup(slot_name)

    def literal_copy(self):
        """
        Create copy such that modifications of the copy will not have any
        influence on the original object.

        This is used to create copy from objects on literal stack, which need
        to stay unchanged.

        Returns:
            Object: Copy of this object.
        """
        obj = Object()
        obj._slot_values = self._slot_values[:]
        obj._parent_slot_values = self._parent_slot_values[:]

        obj.map = self.map
        self.map.used_in_multiple_objects = True

        return obj

    def __str__(self):
        return "Object(%s)" % ", ".join(self.map._slots.keys())


class _ObjectWithMapEncapsulation(_BareObject):
    # map encapsulation - lets pretend that map is not present at all
    @property
    def slot_keys(self):
        return self.map._slots.keys()

    @property
    def parent_slot_keys(self):
        return self.map._parent_slots.keys()

    @property
    def is_block(self):
        return self.map.is_block

    @is_block.setter
    def is_block(self, is_block):
        self.map.is_block = is_block

    @property
    def visited(self):
        return self.map.visited

    @visited.setter
    def visited(self, visited):
        self.map.visited = visited

    @property
    def parameters(self):
        return self.map.parameters

    @parameters.setter
    def parameters(self, new_paremeters):
        assert isinstance(new_paremeters, list)

        new_map = self.map.clone()
        new_map.parameters = new_paremeters
        self.map = new_map

    @property
    def ast(self):
        return self.map.ast

    @ast.setter
    def ast(self, new_ast):
        self.map.ast = new_ast

    @property
    def code_context(self):
        return self.map.code_context

    @code_context.setter
    def code_context(self, new_code_context):
        new_map = self.map.clone()
        new_map.code_context = new_code_context
        self.map = new_map

    @property
    def primitive_code(self):
        return self.map.primitive_code

    @property
    def primitive_code_self(self):
        return self.map.primitive_code_self

    @property
    def has_slots(self):
        return bool(self._slot_values)

    @property
    def has_parents(self):
        return bool(self._parent_slot_values)


class _ObjectWithMetaOperations(_ObjectWithMapEncapsulation):
    def _clone_map_if_used_by_multiple_objects(self):
        if self.map.used_in_multiple_objects:
            self.map = self.map.clone()

    def meta_add_slot(self, slot_name, value, check_duplicates=False):
        """
        check_duplicates: make sure that one value is stored only once
        """
        assert isinstance(value, Object)

        value.scope_parent = self

        if slot_name in self.map._slots:
            self.set_slot(slot_name, value)
            return

        self._clone_map_if_used_by_multiple_objects()

        if not check_duplicates:
            self.map.add_slot(slot_name, len(self._slot_values))
            self._slot_values.append(value)
            return

        if value in self._slot_values:
            self.map.add_slot(slot_name, self._slot_values.index(value))
        else:
            self.map.add_slot(slot_name, len(self._slot_values))
            self._slot_values.append(value)

    def meta_remove_slot(self, slot_name):
        if slot_name not in self.map._slots:
            return

        self._clone_map_if_used_by_multiple_objects()
        slot_index = self.map._slots[slot_name]
        self.map.remove_slot(slot_name)
        self._slot_values.pop(slot_index)

        for name, reference in self.map._slots.iteritems():
            if reference >= slot_index:
                self.map._slots[name] -= 1

    def meta_insert_slot(self, slot_index, slot_name, value):  # TODO: wtf?
        if slot_name in self.map._slots:
            self.set_slot(slot_name, value)

        self._clone_map_if_used_by_multiple_objects()
        self.map.insert_slot(slot_index, slot_name, len(self._slot_values))

        self._slot_values.append(value)

    def meta_add_parent(self, parent_name, value):
        assert isinstance(value, Object)

        if parent_name in self.map._parent_slots:
            index = self.map._parent_slots[parent_name]
            self._parent_slot_values[index] = value
            return

        self._clone_map_if_used_by_multiple_objects()

        self.map.add_parent(parent_name, len(self._parent_slot_values))
        self._parent_slot_values.append(value)

    def meta_get_parent(self, parent_name, alt=None):
        index = self.map._parent_slots.get(parent_name, -1)

        if index == -1:
            return alt

        return self._parent_slot_values[index]

    def meta_remove_parent(self, parent_name):
        if parent_name not in self.map._parent_slots:
            return False

        self._clone_map_if_used_by_multiple_objects()

        parent_index = self.map._parent_slots[parent_name]
        self.map.remove_parent(parent_name)
        self._parent_slot_values.pop(parent_index)

        for name, reference in self.map._parent_slots.iteritems():
            if reference >= parent_index:
                self.map._parent_slots[name] -= 1

    def meta_set_parameters(self, parameters):
        self._clone_map_if_used_by_multiple_objects()
        self.map.parameters = parameters

    def meta_set_ast(self, ast):
        assert isinstance(ast, BaseBox)
        self.map.ast = ast

    def meta_set_code_context(self, code_context):
        self._clone_map_if_used_by_multiple_objects()
        self.map.code_context = code_context


class Object(_ObjectWithMetaOperations):
    pass


class ObjectMap(object):
    def __init__(self):
        self._slots = OrderedDict()
        self._parent_slots = OrderedDict()

        self.visited = False
        self.is_block = False
        self.used_in_multiple_objects = False

        self.ast = None
        self.code_context = None
        self.primitive_code = None
        self.primitive_code_self = None

        self.parameters = []

    def clone(self):
        new_map = ObjectMap()

        new_map.ast = self.ast
        new_map._slots = self._slots.copy()
        new_map.is_block = self.is_block
        new_map.parameters = self.parameters[:]
        new_map.code_context = self.code_context
        new_map._parent_slots = self._parent_slots.copy()
        new_map.primitive_code = self.primitive_code

        return new_map

    # meta-modifications
    def add_slot(self, slot_name, index):
        assert isinstance(index, int)

        self._slots[slot_name] = index

    def remove_slot(self, slot_name):
        if slot_name not in self._slots:
            return False

        del self._slots[slot_name]
        return True

    def insert_slot(self, slot_index, slot_name, index):
        if slot_index < 0:
            slot_index = 0

        if slot_index > len(self._slots):
            self.add_slot(slot_name, index)

        new_slots = OrderedDict()
        for cnt, key in enumerate(self._slots.keys()):
            if cnt == slot_index:
                new_slots[slot_name] = index

            new_slots[key] = self._slots[key]

        self._slots = new_slots

    def add_parent(self, parent_name, index):
        assert isinstance(index, int)

        self._parent_slots[parent_name] = index

    def remove_parent(self, parent_name):
        if parent_name not in self._parent_slots:
            return False

        del self._parent_slots[parent_name]
        return True
