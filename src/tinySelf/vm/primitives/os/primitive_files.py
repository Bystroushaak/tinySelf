# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn

from tinySelf.vm.primitives.cache import ObjCache


class PrimitiveFileObject(Object):
    _OBJ_CACHE = ObjCache()
    _immutable_fields_ = ["value"]
    def __init__(self, value, obj_map=None):
        Object.__init__(self, PrimitiveFileObject._OBJ_CACHE.map)

        assert isinstance(value, str)
        self.value = value

        if PrimitiveFileObject._OBJ_CACHE.map is not None:
            self._slot_values = PrimitiveFileObject._OBJ_CACHE.slots
            return

        if PrimitiveFileObject._OBJ_CACHE.map is None:
            PrimitiveFileObject._OBJ_CACHE.store(self)

    def __str__(self):
        return "FileObject()"  # TODO: add path

    def __eq__(self, obj):
        if not isinstance(obj, PrimitiveFileObject):
            return False

        return self.value == obj.value


def open_file(interpreter, pseudo_self, parameters):
    pass


def open_file_err(interpreter, pseudo_self, parameters):
    pass


def get_primitive_files():
    files_obj = Object()

    add_primitive_fn(files_obj, "open:", open_file, ["path"])
    add_primitive_fn(files_obj, "open:Fails:", open_file_err, ["path", "err"])

    return files_obj
