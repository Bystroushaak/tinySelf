# -*- coding: utf-8 -*-
from rpython.rlib.rsocket import AF_INET
from rpython.rlib.rsocket import SOCK_STREAM
from rpython.rlib.rsocket import RSocket
from rpython.rlib.rsocket import INETAddress

from tinySelf.vm.object_layout import Object

from tinySelf.vm.primitives.cache import ObjCache
from tinySelf.vm.primitives.primitive_int import PrimitiveIntObject
from tinySelf.vm.primitives.primitive_int import PrimitiveStrObject
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn


class PrimitiveINETAddress(Object):
    def __init__(self):
        pass


def socket_recv(interpreter, pseudo_self, parameters):
    size_obj = parameters[0]
    assert isinstance(size_obj, PrimitiveIntObject)
    assert isinstance(pseudo_self, PrimitiveSocketObject)

    return PrimitiveStrObject(pseudo_self.value.recv(int(size_obj.value)))


def socket_sendall(interpreter, pseudo_self, parameters):
    content_obj = parameters[0]
    assert isinstance(content_obj, PrimitiveStrObject)
    assert isinstance(pseudo_self, PrimitiveSocketObject)

    pseudo_self.value.sendall(content_obj.value)
    return pseudo_self


def socket_close(interpreter, pseudo_self, parameters):
    assert isinstance(pseudo_self, PrimitiveSocketObject)

    pseudo_self.value.close()
    return pseudo_self


class PrimitiveSocketObject(Object):
    _OBJ_CACHE = ObjCache()
    _immutable_fields_ = ["value"]
    def __init__(self, value, obj_map=None):
        Object.__init__(self, PrimitiveSocketObject._OBJ_CACHE.map)

        assert isinstance(value, RSocket)
        self.value = value

        if PrimitiveSocketObject._OBJ_CACHE.is_set:
            PrimitiveSocketObject._OBJ_CACHE.restore(self)
            return

        add_primitive_fn(self, "recv:", socket_recv, ["size"])
        add_primitive_fn(self, "sendAll:", socket_sendall, ["data"])
        add_primitive_fn(self, "close", socket_close, [])

        PrimitiveSocketObject._OBJ_CACHE.store(self)

    def __str__(self):
        return "PrimitiveSocket()"

    def __eq__(self, obj):
        if not isinstance(obj, PrimitiveSocketObject):
            return False

        return self.value == obj.value


def open_socket(interpreter, pseudo_self, parameters):
    host_obj = parameters[0]
    assert isinstance(host_obj, PrimitiveStrObject)
    port_obj = parameters[1]
    assert isinstance(port_obj, PrimitiveIntObject)

    # TODO: also add for IPv6 and unix
    addr = INETAddress(host_obj.value, int(port_obj.value))
    socket = RSocket(AF_INET, SOCK_STREAM)
    socket.connect(addr)

    return PrimitiveSocketObject(socket)


def get_primitive_socket():
    socket_obj = Object()

    add_primitive_fn(socket_obj, "open:Port:", open_socket, ["addr", "port"])

    return socket_obj
