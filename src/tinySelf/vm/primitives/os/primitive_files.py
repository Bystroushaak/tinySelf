# -*- coding: utf-8 -*-
import os.path

from rpython.rlib.rfile import RFile
from rpython.rlib.rfile import create_file

from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.primitives import PrimitiveStrObject
from tinySelf.vm.object_layout import Object

from tinySelf.vm.primitives.cache import ObjCache
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn
from tinySelf.vm.primitives.interpreter_primitives import primitive_fn_raise_error
from tinySelf.vm.primitives.interpreter_primitives import run_after_primitive_ends


def close_file(interpreter, pseudo_self, parameters):
    assert isinstance(pseudo_self, PrimitiveFileObject)

    pseudo_self.value.close()
    return pseudo_self


def flush_file(interpreter, pseudo_self, parameters):
    assert isinstance(pseudo_self, PrimitiveFileObject)

    pseudo_self.value.flush()
    return pseudo_self


def tell_file(interpreter, pseudo_self, parameters):
    assert isinstance(pseudo_self, PrimitiveFileObject)

    return PrimitiveIntObject(pseudo_self.value.tell())


class PrimitiveFileObject(Object):
    _OBJ_CACHE = ObjCache()
    _immutable_fields_ = ["value"]
    def __init__(self, value, obj_map=None, path=""):
        Object.__init__(self, PrimitiveFileObject._OBJ_CACHE.map)

        # [translation:ERROR] AttributeError: 'FrozenDesc' object has no attribute
        # 'getuniqueclassdef'
        assert isinstance(value, RFile)
        self.value = value
        self.path = path

        if PrimitiveFileObject._OBJ_CACHE.map is not None:
            self._slot_values = PrimitiveFileObject._OBJ_CACHE.slots
            return

        add_primitive_fn(self, "close", close_file, [])
        add_primitive_fn(self, "flush", flush_file, [])
        add_primitive_fn(self, "tell", tell_file, [])

        if PrimitiveFileObject._OBJ_CACHE.map is None:
            PrimitiveFileObject._OBJ_CACHE.store(self)

    def __str__(self):
        try:
            self.value._check_closed()
            status = ""
        except ValueError:
            status = ", closed"

        # status = ", closed" if self.value.closed else ""
        return "FileObject(%s%s)" % (self.path, status)

    def __eq__(self, obj):
        if not isinstance(obj, PrimitiveFileObject):
            return False

        return self.value == obj.value


def open_file(interpreter, pseudo_self, parameters):
    path_obj = parameters[0]
    assert isinstance(path_obj, PrimitiveStrObject)
    path = path_obj.value

    if os.path.exists(path):
        return PrimitiveFileObject(create_file(path), path=path)

    primitive_fn_raise_error(interpreter, None,
                             [PrimitiveStrObject("File `%s` not found." % path)])


def open_file_err(interpreter, pseudo_self, parameters):
    path_obj = parameters[0]
    assert isinstance(path_obj, PrimitiveStrObject)
    path = path_obj.value
    err_blck = parameters[1]
    assert isinstance(path_obj, Object)

    if os.path.exists(path):
        return PrimitiveFileObject(create_file(path), path=path)

    scope_parent = interpreter.process.frame.self
    run_after_primitive_ends(interpreter, scope_parent, err_blck.get_slot("value"))


def open_file_mode_fails(interpreter, pseudo_self, parameters):
    path_obj = parameters[0]
    assert isinstance(path_obj, PrimitiveStrObject)
    path = path_obj.value
    mode = parameters[1]
    assert isinstance(mode, PrimitiveStrObject)
    err_blck = parameters[2]
    assert isinstance(err_blck, Object)

    scope_parent = interpreter.process.frame.self

    if len(mode.value) != 1 or mode.value[0] not in "rwaU":
        run_after_primitive_ends(interpreter, scope_parent, err_blck.get_slot("value"),
                                 [PrimitiveStrObject("Mode must be r/w/a/U.")])
        return

    if mode.value == "r" and not os.path.exists(path):
        run_after_primitive_ends(interpreter, scope_parent, err_blck.get_slot("value"),
                                 [PrimitiveStrObject("File `%s` doesn't exists!" % path)])
        return

    return PrimitiveFileObject(create_file(path, mode.value), path=path)


def read_file(interpreter, pseudo_self, parameters):
    pass


def read_file_ammount(interpreter, pseudo_self, parameters):
    pass


def write_file(interpreter, pseudo_self, parameters):
    pass


def seek_to(interpreter, pseudo_self, parameters):
    pass


def get_primitive_files():
    files_obj = Object()

    add_primitive_fn(files_obj, "open:", open_file, ["path"])
    add_primitive_fn(files_obj, "open:Fails:", open_file_err, ["path", "err"])
    add_primitive_fn(files_obj, "open:Mode:Fails:", open_file_mode_fails,
                     ["path", "mode", "err"])

    return files_obj
