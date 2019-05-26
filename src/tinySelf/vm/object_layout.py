# -*- coding: utf-8 -*-
from collections import OrderedDict

from rply.token import BaseBox

from tinySelf.config import OBJ_MAP_LAST_NUMBER_OF_VISITED_OBJS
from tinySelf.shared.arrays import TwoPointerArray
from tinySelf.shared.lightweight_dict import LightWeightDict
from tinySelf.shared.lightweight_dict import LightWeightDictObjects


class CachedSlot(object):
    def __init__(self, result, visited_objects):
        self.result = result
        self.visited_objects = visited_objects


class VersionedObject(object):
    def __init__(self, obj):
        self.obj = obj
        self.version = obj.map._version

    def verify(self):
        return self.obj.map._version == self.version


class _BareObject(object):
    def __init__(self, obj_map=None):
        self.map = ObjectMap() if obj_map is None else obj_map
        self._scope_parent = None

        self.visited = False

        self._parent_slot_values = None
        self._slot_values = None

    @property
    def scope_parent(self):
        return self._scope_parent

    @scope_parent.setter
    def scope_parent(self, sp):
        self.map._version += 1
        self._scope_parent = sp

    @property
    def has_code(self):
        return self.map.code_context is not None

    @property
    def has_primitive_code(self):
        return self.map.primitive_code is not None

    @property
    def is_assignment_primitive(self):
        return False

    def set_slot(self, slot_name, value):
        slot_index = self.map._slots.get(slot_name, -1)

        if slot_index == -1:
            return False

        self.map._version += 1

        self._slot_values[slot_index] = value
        return True

    def get_slot(self, slot_name):
        if self._slot_values is None:
            return None

        slot_index = self.map._slots.get(slot_name, -1)

        if slot_index == -1:
            return None

        return self._slot_values[slot_index]

    def parent_lookup(self, slot_name):
        """
        Look for `slot_name` in all parents.

        Args:
            slot_name (str): Name of the slot to look for.

        Returns:
            obj: Object instance or None if not found.

        Raises:
            KeyError: If multiple slots are found.
        """
        result = self._cached_lookup(slot_name)
        if result is not None:
            return result

        objects = TwoPointerArray(self.map._last_number_of_visited_objects)
        objects.append(self)

        result = None
        visited_objects = TwoPointerArray(self.map._last_number_of_visited_objects)
        while len(objects) > 0:
            obj = objects.pop_first()

            if obj.visited:
                continue

            obj.visited = True
            visited_objects.append(obj)

            slot = obj.get_slot(slot_name)
            if slot is not None:
                if result is not None:
                    raise KeyError("Too many parent slots `%s`, use resend!" % slot_name)

                result = slot
                continue

            if obj.scope_parent is not None and not obj.scope_parent.visited:
                objects.append(obj.scope_parent)

            # objects.extend(obj._parent_slot_values)
            # this if actually produces faster code
            if obj._parent_slot_values is not None:
                for parent in obj._parent_slot_values:
                    if not parent.visited:
                        objects.append(parent)

        visited_as_list = visited_objects.to_list()
        for obj in visited_as_list:
            obj.visited = False

        self.map._last_number_of_visited_objects = len(visited_objects)

        if result is not None:
            self._store_to_parent_cache(slot_name, result, visited_as_list)

        return result

    def _store_to_parent_cache(self, slot_name, result, visited_as_list):
        if self.map._parent_cache is None:
            self.map._parent_cache = LightWeightDictObjects()

        self.map._parent_cache.set(
            slot_name,
            CachedSlot(result, [VersionedObject(x) for x in visited_as_list])
        )

    def _cached_lookup(self, slot_name):
        if self.map._parent_cache is None:
            return None

        cached_result = self.map._parent_cache.get(slot_name)
        if cached_result is None:
            return None

        prealocate_size = len(cached_result.visited_objects) + 10
        objects = TwoPointerArray(prealocate_size)
        visited_objects = TwoPointerArray(prealocate_size)

        for item in cached_result.visited_objects:
            if item.verify():
                item.obj.visited = True
                visited_objects.append(item.obj)
            else:
                item.obj.visited = False
                objects.append(item.obj)

        if not self.visited:
            objects.append(self)
        else:
            visited_objects.append(self)

        result = cached_result.result
        while len(objects) > 0:
            obj = objects.pop_first()
            visited_objects.append(obj)

            if obj.visited:
                continue

            obj.visited = True

            if obj.scope_parent is not None and not obj.scope_parent.visited:
                objects.append(obj.scope_parent)

            # objects_to_visit.extend(obj._parent_slot_values)
            # this if actually produces faster code
            if obj._parent_slot_values is not None:
                for parent in obj._parent_slot_values:
                    if not parent.visited:
                        objects.append(parent)

            slot = obj.get_slot(slot_name)
            if slot is not None:
                result = slot
                continue

        for obj in visited_objects.to_list():
            obj.visited = False

        return result

    def slot_lookup(self, slot_name):
        """
        Look for the slot_name in own slots, if not found, delegate the search
        to the parents.

        First value of the returned tuple indicates whether the slot was found
        in the object directly (=True), or in the parent (=False).

        Args:
            slot_name (str): ...

        Returns:
            tuple: (bool: Was in obj?, Object: Resolved Object or None)
        """
        assert isinstance(slot_name, str)

        if self._slot_values is not None:
            slot_index = self.map._slots.get(slot_name, -1)

            if slot_index != -1:
                return True, self._slot_values[slot_index]

        if self.scope_parent is not None:
            obj = self.scope_parent.get_slot(slot_name)

            if obj is not None:
                return False, obj

        return False, self.parent_lookup(slot_name)

    def clone(self):
        obj = Object(obj_map=self.map)

        if self._slot_values is not None:
            obj._slot_values = self._slot_values[:]
        if self._parent_slot_values is not None:
            obj._parent_slot_values = self._parent_slot_values[:]

        obj.scope_parent = self.scope_parent
        self.map._used_in_multiple_objects = True

        return obj

    def __str__(self):
        if self.map.is_block:
            return "Block(%s)" % ", ".join(self.map._slots.keys())

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
    def expensive_parent_slots(self):
        return OrderedDict(
            (key, self._parent_slot_values[self.map._parent_slots[key]])
            for key in self.parent_slot_keys
        )

    @property
    def is_block(self):
        return self.map.is_block

    @is_block.setter
    def is_block(self, is_block):
        self.map.is_block = is_block

    @property
    def parameters(self):
        return self.map.parameters

    @parameters.setter
    def parameters(self, new_paremeters):
        assert isinstance(new_paremeters, list)

        self._clone_map_if_used_by_multiple_objects()
        self.map.parameters = new_paremeters

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
    def code_context(self, new_code_context):  # TODO: add guard if used in multiple objects
        new_map = self.map.clone()
        new_map.code_context = new_code_context
        self.map = new_map

    @property
    def primitive_code(self):
        return self.map.primitive_code

    @property
    def has_slots(self):
        return bool(self._slot_values)

    @property
    def will_have_slots(self):
        if self.map.code_context is not None:
            return self.map.code_context.will_have_slots

        return False

    @property
    def has_parents(self):
        return bool(self._parent_slot_values)

    def _clone_map_if_used_by_multiple_objects(self):
        if self.map._used_in_multiple_objects:
            self.map = self.map.clone()


class _ObjectWithMetaOperations(_ObjectWithMapEncapsulation):
    def meta_add_slot(self, slot_name, value, check_duplicates=False):
        """
        check_duplicates: make sure that one value is stored only once
        """
        assert isinstance(value, Object)

        value.scope_parent = self

        if self.map._slots.has_key(slot_name):
            self.set_slot(slot_name, value)
            self.map._version += 1
            return

        self._clone_map_if_used_by_multiple_objects()

        if self._slot_values is None:
            self._slot_values = []

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
        if not self.map._slots.has_key(slot_name):
            return

        self._clone_map_if_used_by_multiple_objects()

        slot_index = self.map._slots[slot_name]
        self.map.remove_slot(slot_name)
        self._slot_values.pop(slot_index)

        for name, reference in self.map._slots.iteritems():
            if reference >= slot_index:
                self.map._slots[name] -= 1

    def meta_insert_slot(self, slot_index, slot_name, value):  # TODO: wtf?
        if self.map._slots.has_key(slot_name):
            self.set_slot(slot_name, value)
            self.map._version += 1
            return

        self._clone_map_if_used_by_multiple_objects()

        if self._slot_values is None:
            self._slot_values = []

        self.map.insert_slot(slot_index, slot_name, len(self._slot_values))

        self._slot_values.append(value)

    def meta_add_parent(self, parent_name, value):
        assert isinstance(value, Object)

        if self.map._parent_slots.has_key(parent_name):
            index = self.map._parent_slots[parent_name]
            self._parent_slot_values[index] = value
            self.map._version += 1
            return

        self._clone_map_if_used_by_multiple_objects()

        if self._parent_slot_values is None:
            self._parent_slot_values = []

        self.map.add_parent(parent_name, len(self._parent_slot_values))
        self._parent_slot_values.append(value)

    def meta_get_parent(self, parent_name, alt=None):
        if self._parent_slot_values is None:
            return alt

        index = self.map._parent_slots.get(parent_name, -1)

        if index == -1:
            return alt

        return self._parent_slot_values[index]

    def meta_remove_parent(self, parent_name):
        if not self.map._parent_slots.has_key(parent_name):
            return

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
        self._slots = LightWeightDict()
        self._parent_slots = LightWeightDict()
        self._used_in_multiple_objects = False

        self._version = 0
        self._parent_cache = None
        self._last_number_of_visited_objects = OBJ_MAP_LAST_NUMBER_OF_VISITED_OBJS

        self.is_block = False

        self.ast = None
        self.code_context = None
        self.primitive_code = None

        self.parameters = []

    def clone(self):
        new_map = ObjectMap()

        new_map._slots = self._slots.copy()
        new_map._parent_slots = self._parent_slots.copy()

        new_map.ast = self.ast
        new_map.is_block = self.is_block
        new_map.parameters = self.parameters[:]

        new_map._version = self._version
        if self._parent_cache is not None:
            new_map._parent_cache = self._parent_cache.copy()

        if self.code_context is not None:
            new_map.code_context = self.code_context #.clone()

        new_map.primitive_code = self.primitive_code

        return new_map

    # meta-modifications
    def add_slot(self, slot_name, index):
        assert isinstance(index, int)

        self._slots[slot_name] = index
        self._version += 1

    def remove_slot(self, slot_name):
        if slot_name not in self._slots:
            return False

        del self._slots[slot_name]
        self._version += 1

        return True

    def insert_slot(self, slot_index, slot_name, index):
        if slot_index < 0:
            slot_index = 0

        if slot_index > len(self._slots):
            self.add_slot(slot_name, index)

        new_slots = LightWeightDict()
        for cnt, key in enumerate(self._slots.keys()):
            if cnt == slot_index:
                new_slots[slot_name] = index

            new_slots[key] = self._slots[key]

        self._slots = new_slots
        self._version += 1

    def add_parent(self, parent_name, index):
        assert isinstance(index, int)

        self._parent_slots[parent_name] = index
        self._version += 1

    def remove_parent(self, parent_name):
        if not self._parent_slots.has_key(parent_name):
            return False

        del self._parent_slots[parent_name]
        self._version += 1

        return True
