# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object


def _build_primitive_code_obj(primitive_fn, arguments):
    code_obj = Object()

    code_obj.map.arguments = arguments
    code_obj.map.primitive_code = primitive_fn

    return code_obj


def _add_primitive_fn(obj, slot_name, primitive_fn, arguments):
    primitive_code_obj = _build_primitive_code_obj(primitive_fn, arguments)
    obj.meta_add_slot(slot_name, primitive_code_obj)


class PrimitiveIntObject(Object):
    def __init__(self, value, obj_map=None):
        super(PrimitiveIntObject, self).__init__(obj_map)

        self.value = value

        _add_primitive_fn(self, "+", self._add, ["obj"])

    def _add(self, obj):
        assert isinstance(obj, PrimitiveIntObject)

        return PrimitiveIntObject(self.value + obj.value)

    def __eq__(self, obj):
        if not hasattr(obj, "value"):
            return False

        return self.value == obj.value

    def __str__(self):
        return "PrimitiveIntObject(%d)" % self.value


class PrimitiveStrObject(Object):
    def __init__(self, value, obj_map=None):
        super(PrimitiveStrObject, self).__init__(obj_map)

        self.value = value

        _add_primitive_fn(self, "+", self._add, ["obj"])

    def _add(self, obj):
        assert isinstance(obj, PrimitiveStrObject)

        return PrimitiveStrObject(self.value + obj.value)

    def __str__(self):
        return "PrimitiveStrObject(%s)" % self.value


class PrimitiveNilObjectSingleton(Object):
    def __init__(self):
        super(PrimitiveNilObjectSingleton, self).__init__()

    def __str__(self):
        return "PrimitiveNilObject()"


_NIL_OBJ = PrimitiveNilObjectSingleton()
def PrimitiveNilObject(*args, **kwargs):
    return _NIL_OBJ


class AssignmentPrimitive(Object):
    def __init__(self, real_parent=None):
        self.real_parent = real_parent

    @property
    def is_assignment_primitive(self):
        return True

    @property
    def has_code(self):
        return False

    @property
    def has_primitive_code(self):
        return False

    def __str__(self):
        return "AssignmentPrimitive()"


def add_block_trait(block):
    obj = Object()
    obj.meta_add_slot("value", block)
    obj.meta_add_slot("with:", block)
    obj.meta_add_slot("with:With:", block)
    obj.meta_add_slot("with:With:With:", block)
    obj.meta_add_slot("with:With:With:With:", block)
    obj.meta_add_slot("withAll:", block)

    return obj


# def _primitive_create_mirror(obj):
#     def list_slots():
#         for slot_name in obj.map.slots.keys():
#             pass

#     mirror_obj = Object()
#     mirror_obj.meta_add_slot("mirroredObj", obj)



def get_primitives():
    """
    Return object with primitive functions mapped to its slots.

    Returns:
        obj: Instance of tinySelf's Object.
    """
    primitives = Object()
    _add_primitive_fn(primitives, "primitiveInt", PrimitiveIntObject, "literal")
    _add_primitive_fn(primitives, "primitiveStr", PrimitiveStrObject, "literal")
    primitives.meta_add_slot("primitiveNil", PrimitiveNilObject())

    # _add_primitive(primitives, "mirrorOn:", _primitive_create_mirror, ["obj"])

    return primitives
