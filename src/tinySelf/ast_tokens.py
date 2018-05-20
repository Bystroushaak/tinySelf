#! /usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# from collections import OrderedDict

from rply.token import BaseBox


def _repr_list(l):
    results = []
    for x in l:
        assert isinstance(x, BaseBox)
        results.append(x.__str__())

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

    def __str__(self):
        return "\n".join([x.__str__() for x in self.ast])


class Self(BaseBox):
    def __eq__(self, obj):
        return isinstance(obj, self.__class__)

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        return "Self()"


class Nil(Self):
    def __str__(self):
        return "Nil()"


class Object(BaseBox):
    def __init__(self, slots=None, params=None, code=None, parents=None):
        self.slots = {}
        self.params = []
        self.code = []
        self.parents = {}

        if slots is not None:
            self.slots.update(slots)
        if params is not None:
            self.params.extend(params)
        if code is not None:
            self.code.extend(code)
        if parents is not None:
            self.parents.update(parents)

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
            assert isinstance(self.params[0], BaseBox)
            parameters.append("params=" + _repr_list(self.params))
        if self.code:
            assert isinstance(self.code[0], BaseBox)
            parameters.append("code=" + _repr_list(self.code))
        if self.parents:
            parameters.append("parents=" + _repr_dict(self.parents))

        return "%s(%s)" % (self.__class__.__name__, ", ".join(parameters))


class Block(Object):
    pass


class Number(BaseBox):  # TODO: remove
    def __init__(self, value):
        self.value = value

    def eval(self):
        return self.value

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

    def eval(self):
        return self.value

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
            params = _repr_list(self.parameters)

        return "KeywordMessage(name=%s, parameters=%s)" % (self.name, params)


class BinaryMessage(BaseBox):
    def __init__(self, name, parameter):
        self.name = name
        self.parameter = parameter

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

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.obj == obj.obj and \
               self.msgs == obj.msgs

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        msgs = "[]"
        if self.msgs:
            msgs = _repr_list(self.msgs)

        return "Cascade(obj=%s, msgs=%s)" % (self.obj.__str__(), msgs)


class Return(BaseBox):
    def __init__(self, value):
        self.value = value

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
