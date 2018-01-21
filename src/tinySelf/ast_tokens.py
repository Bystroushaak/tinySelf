#! /usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
from rply.token import BaseBox


class Self(BaseBox):
    def __eq__(self, obj):
        return isinstance(obj, self.__class__)

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __repr__(self):
        return "Self()"


class Object(BaseBox):
    def __init__(self, slots=None, params=None, code=None, parents=None):
        self.slots = slots
        self.params = params
        self.code = code
        self.parents = parents

        # mutable parameters strikes again
        if not slots:
            self.slots = {}
        if not params:
            self.params = []
        if not code:
            self.code = []
        if not parents:
            self.parents = {}

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.slots == obj.slots and \
               self.params == obj.params and \
               self.code == obj.code

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __repr__(self):
        parameters = []

        if self.slots:
            parameters.append("slots=%r" % self.slots)
        if self.params:
            parameters.append("params=%r" % self.params)
        if self.code:
            parameters.append("code=%r" % self.code)
        if self.parents:
            parameters.append("parents=%r" % self.parents)

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

    def __repr__(self):
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


class Message(BaseBox):
    def __init__(self, name):
        self.name = name

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.name == obj.name

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __repr__(self):
        return "Message(%r)" % self.name


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

    def __repr__(self):
        return "KeywordMessage(name=%r, parameters=%r)" % (self.name, self.parameters)


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

    def __repr__(self):
        return "BinaryMessage(name=%r, parameter=%r)" % (self.name, self.parameter)


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

    def __repr__(self):
        return "Send(obj=%r, msg=%r)" % (self.obj, self.msg)


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

    def __repr__(self):
        return "Cascade(obj=%s, msgs=%s)" % (
            repr(self.obj),
            repr([x for x in self.msgs])
        )


class Return(BaseBox):
    def __init__(self, value):
        self.value = value

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.value == obj.value

    def __ne__(self, obj):
        return not self.__eq__(obj)


class AssignmentPrimitive(BaseBox):
    def __eq__(self, obj):
        return isinstance(obj, self.__class__)

    def __ne__(self, obj):
        return not self.__eq__(obj)
