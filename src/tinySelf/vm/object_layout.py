# -*- coding: utf-8 -*-
class Object(object):
    def __init__(self, obj_map=None):
        if obj_map is None:
            obj_map = ObjectMap()

        self.map = obj_map
        self.parents = []

        self.slots_references = []

    def clone(self):
        o = Object(obj_map=self.map)
        o.slots_references = self.slots_references[:]
        return o

    def set_slot(self, slot_name, value):
        slot_index = self.map.get(slot_name, None)

        if slot_index is None:
            return False

        self.slots_references[slot_index] = value
        return True

    def get_slot(self, slot_name):
        slot_index = self.map.get(slot_name, None)
        if slot_index is None:
            return None

        return self.slots_references[slot_index]

    # meta operations
    def meta_add_slot(self, slot_name, value):  # TODO: support auto Nil value
        if slot_name in self.map:
            return self.set_slot(slot_name, value)

        new_map = self.map.clone()
        is_slot_added = new_map.add_slot(slot_name, len(self.slots_references))

        if is_slot_added:
            self.slots_references.append(value)
            self.map = new_map

        return is_slot_added

    def meta_remove_slot(self, slot_name):
        if slot_name not in self.map:
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
                    new_slots_references[i+1] = self.slots_references[i]

            self.slots_references = new_slots_references
            self.map = new_map

        return is_slot_inserted


class ObjectMap(object):
    def __init__(self):
        # self.parents = set()
        # self.parent_slots = parent_slots
        self.slots = {}

    def clone_map(self):
        new_map = ObjectMap()
        new_map.slots = self.slots.copy()
        return new_map

    # meta-modifications
    def add_slot(self, slot_name, index):
        self.slots[slot_name] = index

        return True

    def delete_slot(self, slot_name):
        del self.slots.slots[slot_name]
        return True

    def insert_slot(self, slot_name, index):
        new_slots = {}
        for cnt, key in enumerate(self.slots.keys()):
            if cnt == index:
                new_slots[slot_name] = index

            new_slots[key] = self.slots[key]

        return True
