# -*- coding: utf-8 -*-
from collections import OrderedDict

from rply.token import BaseBox

from tinySelf.vm.bytecodes import *


def _repr_list_of_baseboxes(l):
    results = []
    for x in l:
        assert isinstance(x, BaseBox)
        results.append(x.__str__())

    return "[" + ", ".join(results) + "]"


def _repr_list_of_strs(l):
    results = []
    for x in l:
        assert isinstance(x, str)
        results.append(x)

    return "[" + ", ".join(results) + "]"


def _repr_dict(d):
    results = []
    for k, v in d.iteritems():
        assert isinstance(k, str)
        assert isinstance(v, BaseBox)
        results.append("%s: %s" % (k, v.__str__()))

    return "{" + ", ".join(results) + "}"


class Root(BaseBox):
    def __init__(self, tree=[]):
        self.ast = tree

    def compile(self, context):
        for item in self.ast:
            item.compile(context)

        return context

    def __str__(self):
        return "\n".join([x.__str__() for x in self.ast])


class Self(BaseBox):
    def compile(self, context):
        context.add_bytecode(BYTECODE_PUSHSELF)

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__)

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        return "Self()"


class Nil(Self):
    def compile(self, context):
        context.add_bytecode(BYTECODE_PUSHLITERAL)
        context.add_bytecode(LITERAL_TYPE_NIL)
        context.add_bytecode(0)

        return context

    def __str__(self):
        return "Nil()"


class Object(BaseBox):
    def __init__(self, slots=None, params=None, code=None, parents=None):
        self.slots = OrderedDict()
        self.params = []
        self.code = []
        self.parents = OrderedDict()

        if slots is not None:
            self.slots.update(slots)
        if params is not None:
            self.params.extend(params)
        if code is not None:
            self.code.extend(code)
        if parents is not None:
            self.parents.update(parents)

    def compile(self, context):
        # TODO: compile objects

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.slots == obj.slots and \
               self.params == obj.params and \
               self.code == obj.code and \
               self.parents == obj.parents

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        parameters = []

        if self.slots:
            parameters.append("slots=" + _repr_dict(self.slots))
        if self.params:
            assert isinstance(self.params[0], str)
            parameters.append("params=" + _repr_list_of_strs(self.params))
        if self.code:
            assert isinstance(self.code[0], BaseBox)
            parameters.append("code=" + _repr_list_of_baseboxes(self.code))
        if self.parents:
            parameters.append("parents=" + _repr_dict(self.parents))

        return "%s(%s)" % (self.__class__.__name__, ", ".join(parameters))


class Block(Object):
    def compile(self, context):
        # TODO: compile blocks

        return context


class Number(BaseBox):  # TODO: remove
    def __init__(self, value):
        self.value = value

    def compile(self, context):
        index = context.add_literal_int(self.value)

        context.add_bytecode(BYTECODE_PUSHLITERAL)
        context.add_bytecode(LITERAL_TYPE_INT)
        context.add_bytecode(index)

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.value == obj.value

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        return "Number(%s)" % self.value


class String(BaseBox):  # TODO: remove?
    def __init__(self, value):
        self.value = value

    def compile(self, context):
        index = context.add_literal_str(self.value)

        context.add_bytecode(BYTECODE_PUSHLITERAL)
        context.add_bytecode(LITERAL_TYPE_STR)
        context.add_bytecode(index)

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.value == obj.value

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        return "'%s'" % self.value  # TODO: escaping


class Message(BaseBox):
    def __init__(self, name):
        self.name = name

    def compile(self, context):
        context.add_literal_str_push_bytecode(self.name)

        context.add_bytecode(BYTECODE_SEND)
        context.add_bytecode(SEND_TYPE_UNARY)
        context.add_bytecode(0)

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.name == obj.name

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        return "Message(%s)" % self.name


class KeywordMessage(BaseBox):
    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters

    def compile(self, context):
        context.add_literal_str_push_bytecode(self.name)

        for parameter in self.parameters:
            parameter.compile(context)

        context.add_bytecode(BYTECODE_SEND)
        context.add_bytecode(SEND_TYPE_KEYWORD)
        context.add_bytecode(len(self.parameters))

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.name == obj.name and \
               self.parameters == obj.parameters

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        params = "[]"
        if self.parameters:
            assert isinstance(self.parameters[0], BaseBox)
            params = _repr_list_of_baseboxes(self.parameters)

        return "KeywordMessage(name=%s, parameters=%s)" % (self.name, params)


class BinaryMessage(BaseBox):
    def __init__(self, name, parameter):
        self.name = name
        self.parameter = parameter

    def compile(self, context):
        context.add_literal_str_push_bytecode(self.name)

        self.parameter.compile(context)

        context.add_bytecode(BYTECODE_SEND)
        context.add_bytecode(SEND_TYPE_BINARY)
        context.add_bytecode(1)

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.name == obj.name and \
               self.parameter == obj.parameter

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        return "BinaryMessage(name=%s, parameter=%s)" % (
            self.name,
            self.parameter.__str__()
        )


class Send(BaseBox):
    def __init__(self, obj, msg):
        self.obj = obj
        self.msg = msg

    def compile(self, context):
        self.obj.compile(context)
        self.msg.compile(context)

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.obj == obj.obj and \
               self.msg == obj.msg

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        return "Send(obj=%s, msg=%s)" % (
            self.obj.__str__(),
            self.msg.__str__()
        )


class Cascade(BaseBox):
    def __init__(self, obj, msgs):
        self.obj = obj
        self.msgs = msgs

    def compile(self, context):
        for msg in self.msgs:
            self.obj.compile(context)
            msg.compile(context)

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.obj == obj.obj and \
               self.msgs == obj.msgs

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        msgs = "[]"
        if self.msgs:
            msgs = _repr_list_of_baseboxes(self.msgs)

        return "Cascade(obj=%s, msgs=%s)" % (self.obj.__str__(), msgs)


class Return(BaseBox):
    def __init__(self, value):
        self.value = value

    def compile(self, context):
        self.value.compile(context)
        # context.add_bytecode(BYTECODE_RETURNIMPLICIT)
        context.add_bytecode(BYTECODE_RETURNTOP)

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.value == obj.value

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        return "Return(%s)" % self.value.__str__()


class AssignmentPrimitive(BaseBox):
    def __eq__(self, obj):
        return isinstance(obj, self.__class__)

    def __ne__(self, obj):
        return not self.__eq__(obj)
