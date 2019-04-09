# -*- coding: utf-8 -*-
from collections import OrderedDict

from rply.token import BaseBox

from tinySelf.datastructures.lightweight_dict import LightWeightDict
from tinySelf.datastructures.lightweight_dict import LightWeightDictObjects


class PathHolder(object):
    def __init__(self, obj, path):
        self.obj = obj
        self.path = path

    @staticmethod
    def from_path(obj, new_path, path_holder):
        path = path_holder.path
        path.append(new_path)

        return PathHolder(obj, path)


class VersionedObject(object):
    def __init__(self, object):
        self.object = object
        self.version = object.map._version

    def verify(self):
        return self.object.map._version == self.version


class NamedCacheItem(object):
    def __init__(self, item, objects):
        self.item = item
        self.object_versions = [VersionedObject(x) for x in objects]

    def verify_version(self):
        for x in self.object_versions:
            if not x.verify():
                return False

        return True


def unvisit(visited_objects):
    for obj in visited_objects:
        obj.visited = False


class _BareObject(object):
    def __init__(self, obj_map=None):
        if obj_map is None:
            obj_map = ObjectMap()

        self.map = obj_map
        self.scope_parent = None

        self.visited = False

        self._local_lookups = 0

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

    def set_slot(self, slot_name, value):
        slot_index = self.map._slots.get(slot_name, -1)

        if slot_index == -1:
            return False

        self._slot_values[slot_index] = value
        return True

    def get_slot(self, slot_name):
        slot_index = self.map._slots.get(slot_name, -1)

        if slot_index == -1:
            return None

        return self._slot_values[slot_index]

    @property
    def _parent_cache(self):
        if self.map.code_context is None:
            return None

        return self.map.code_context._parent_cache

    @_parent_cache.setter
    def _parent_cache(self, new_parent_cache):
        self.map.code_context._parent_cache = new_parent_cache

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
        if self._parent_cache is not None:
            result = self._parent_cache.get(slot_name)
            if result is not None:
                if result.verify_version():
                    return result.item
                else:
                    self._parent_cache.delete(slot_name)

        objects = []
        if self.scope_parent is not None and not self.scope_parent.visited:
            objects.append(PathHolder(self.scope_parent, [-1]))

        # objects.extend(self._parent_slot_values)
        if len(self._parent_slot_values) > 0:  # this actually produces faster code
            for cnt, parent in enumerate(self._parent_slot_values):
                objects.append(PathHolder(parent, [cnt]))

        result = None
        result_path = []
        visited_objects = []
        while len(objects) > 0:
            ph = objects.pop(0)

            if ph.obj.visited:
                continue

            ph.obj.visited = True
            visited_objects.append(ph.obj)

            slot = ph.obj.get_slot(slot_name)
            if slot is not None:
                if result is not None:
                    raise KeyError("Too many parent slots `%s`, use resend!" % slot_name)

                result = slot
                result_path = ph.path
                continue

            if ph.obj.scope_parent is not None:
                objects.append(PathHolder.from_path(ph.obj.scope_parent, -1, ph))

            # objects.extend(obj._parent_slot_values)
            if len(ph.obj._parent_slot_values) > 0:  # this actually produces faster code
                for cnt, parent in enumerate(ph.obj._parent_slot_values):
                    objects.append(PathHolder.from_path(parent, cnt, ph))

        unvisit(visited_objects)
        if self.map.code_context is not None:
            if self._parent_cache is None:
                self._parent_cache = LightWeightDictObjects()

            self._parent_cache.set(slot_name, NamedCacheItem(result, visited_objects))

        return result

    def parent_lookup2(self, slot_name):
        """
        Look for `slot_name` in all parents.

        Args:
            slot_name (str): Name of the slot to look for.

        Returns:
            obj: Object instance or None if not found.

        Raises:
            KeyError: If multiple slots are found.
        """
        objects = []
        if self.scope_parent is not None and not self.scope_parent.visited:
            objects.append(self.scope_parent)

        objects.extend(self._parent_slot_values)

        result = None
        visited_objects = []
        while objects:
            obj = objects.pop(0)

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

            if obj.scope_parent is not None:
                objects.append(obj.scope_parent)

            objects.extend(obj._parent_slot_values)

        unvisit(visited_objects)

        return result

    def slot_lookup(self, slot_name, local_lookup_cache=False):
        """
        Look for the slot_name in own slots, if not found, delagate the search
        to the parents.

        Args:
            slot_name (str): ...
            local_lookup_cache (bool, default False): Count lookups and trigger
                dynamic recompilation on frequent access.

        Returns:
            obj: Resolved Object, or None.
        """
        assert isinstance(slot_name, str)

        slot_index = self.map._slots.get(slot_name, -1)

        if slot_index != -1:
            if local_lookup_cache:
                self._local_cache_counter()

            return self._slot_values[slot_index]

        if self.scope_parent is not None:
            obj = self.scope_parent.get_slot(slot_name)

            if obj is not None:
                return obj

        return self.parent_lookup(slot_name)

    def _local_cache_counter(self):
        self._local_lookups += 1

        if self._local_lookups < 5:  # TODO: set dynamically
            return

        if self.map.code_context and not self.map.code_context.recompile:
            self.map.code_context.recompile = True

    def clone(self):
        obj = Object(obj_map=self.map)
        obj._slot_values = self._slot_values[:]
        obj._parent_slot_values = self._parent_slot_values[:]
        obj.scope_parent = self.scope_parent
        self.map._used_in_multiple_objects = True

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
    def meta_add_slot(self, slot_name, value, check_duplicates=False):
        """
        check_duplicates: make sure that one value is stored only once
        """
        assert isinstance(value, Object)

        value.scope_parent = self

        if self.map._slots.has_key(slot_name):
            self.set_slot(slot_name, value)
            self.map._on_structural_changes()
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
            self.map._on_structural_changes()
            return

        self._clone_map_if_used_by_multiple_objects()

        self.map.insert_slot(slot_index, slot_name, len(self._slot_values))

        self._slot_values.append(value)

    def meta_add_parent(self, parent_name, value):
        assert isinstance(value, Object)

        if self.map._parent_slots.has_key(parent_name):
            index = self.map._parent_slots[parent_name]
            self._parent_slot_values[index] = value
            self.map._on_structural_changes()
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

    def _clone_map_if_used_by_multiple_objects(self):
        if self.map._used_in_multiple_objects:
            self.map = self.map.clone()


class Object(_ObjectWithMetaOperations):
    pass


class ObjectMap(object):
    def __init__(self):
        self._slots = LightWeightDict()
        self._parent_slots = LightWeightDict()
        self._used_in_multiple_objects = False
        self._version = 0
        self._parent_cache = None

        self.is_block = False

        self.ast = None
        self.code_context = None
        self.primitive_code = None
        self.primitive_code_self = None

        self.parameters = []

    def clone(self):
        new_map = ObjectMap()

        new_map._slots = self._slots.copy()
        new_map._parent_slots = self._parent_slots.copy()

        new_map.ast = self.ast
        new_map.is_block = self.is_block
        new_map.parameters = self.parameters[:]
        new_map.code_context = self.code_context
        new_map.primitive_code = self.primitive_code

        return new_map

    # meta-modifications
    def add_slot(self, slot_name, index):
        assert isinstance(index, int)

        self._slots[slot_name] = index
        self._on_structural_changes()

    def remove_slot(self, slot_name):
        if slot_name not in self._slots:
            return False

        del self._slots[slot_name]
        self._on_structural_changes()

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
        self._on_structural_changes()

    def add_parent(self, parent_name, index):
        assert isinstance(index, int)

        self._parent_slots[parent_name] = index
        self._on_structural_changes()

    def remove_parent(self, parent_name):
        if not self._parent_slots.has_key(parent_name):
            return False

        del self._parent_slots[parent_name]
        self._on_structural_changes()

        return True

    def _on_structural_changes(self):
        self.invalidate_cache()
        self._version += 1

    def invalidate_cache(self):
        """
        Invalidate dynamic caches in code context objects on meta-operations.
        """
        if self.code_context is not None and self.code_context.is_recompiled:
            self.code_context.invalidate_bytecodes()
