# -*- coding: utf-8 -*-
ADD = 0
DELETE = 1
INSERT = 2


class ObjectMap(object):
    def __init__(self):
        # self.parents = set()
        # self.parent_slots = parent_slots
        self.slots = {}

        self.new_map = None
        self.action = None
        self.action_key = None
        self.action_operand = None

    def get(self, slot_name):
        return self.slots.get(slot_name)

    def set(self, slot_name, value):
        if slot_name in self.slots:
            self.slots[slot_name] = value
            return True

        return False

    # meta-modifications
    def clone_map(self):
        new_map = ObjectMap()

        for k, v in self.slots.items():
            new_map.slots[k] = v

        return new_map

    def update_object_to_new_map(self, o):
        if self.action == ADD:
            o.slots_references.append(self.action_operand)
        elif self.action == DELETE:
            o.slots_references = [
                x for cnt, x in enumerate(o.slots_references)
                if cnt != self.action_key
            ]
        elif self.action == INSERT:
            new_slots = []
            for cnt, x in enumerate(o.slots_references):
                if cnt == self.action_key:
                    new_slots.append(self.action_operand)

                new_slots.append(x)

        o.map = self.new_map

    def insert(self, slot_name, value, index):
        pass

    def add(self, slot_name, value):
        if slot_name in self.slots:
            return self.set(slot_name, value)

        self.action = ADD
        self.action_operand = value

        new_map = self.clone_map()
        new_map.slots[slot_name] = value
        self.new_map = new_map

        return True

    def delete(self, slot_name):
        if slot_name not in self.slots:
            return False

        self.action = DELETE
        self.action_key = self.slots.values().find(slot_name)

        new_map = self.clone_map()
        del new_map.slots[slot_name]
        self.new_map = new_map

        return True


class Object(object):
    def __init__(self, map=None):
        self.map = map
        self.parents = []

        self.slots_references = []

    def clone(self):
        o = self.map.clone()
        o.slots_references = self.slots_references[:]
        return o
