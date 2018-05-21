# -*- coding: utf-8 -*-
from rpython.rlib.objectmodel import cast_object_to_weakaddress


class ObjectMap(object):
    def __inti__(self, parents):
        self.parents = set()

        self.parent_slots = parent_slots
        self.slots = {}

        self.instances = set()

    @classmethod
    def create_map(cls):
        pass

    def clone(self):
        o = Object(map=self)
        self.instances.add(cast_object_to_weakaddress(o))

        return o

    def remove_instance(self, weak_ref):
        self.instances.remove(weak_ref)


class Object(object):
    def __init__(self, map=None):
        self.map = map
        self.slots_references = []

    def clone(self):
        if self.map is None:  #HM, blbost
            self.map = ObjectMap.create_map(self)

        o = self.map.clone()
        o.slots_references = self.slots_references[:]
        return o
