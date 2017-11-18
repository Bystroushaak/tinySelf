#! /usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
from rply.token import BaseBox


class Self(BaseBox):
    def __init__(self):
        pass

    def __eq__(self, obj):
        return isinstance(obj, self.__class__)

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __repr__(self):
        return "Self()"


class Object(BaseBox):
    def __init__(self, slots=None, params=None, code=None):
        self.slots = slots
        self.params = params
        self.code = code

        # mutable parameters strikes again
        if not slots:
            self.slots = {}
        if not params:
            self.params = []
        if not code:
            self.code = []

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.slots == obj.slots and \
               self.params == obj.params and \
               self.code == obj.code

    def __ne__(self, obj):
        return not self.__eq__(obj)


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


class String(BaseBox):  # TODO: remove
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
        return "Send(%s, %s)" % (self.obj, self.msg)
