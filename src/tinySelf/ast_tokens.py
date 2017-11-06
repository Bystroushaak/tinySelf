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


class Object(BaseBox):
    def __init__(self, slots={}, code=[]):
        self.slots = slots
        self.code = code


class Block(Object):
    pass


class Number(BaseBox):  # TODO: remove
    def __init__(self, value):
        self.value = value

    def eval(self):
        return self.value


class String(BaseBox):  # TODO: remove
    def __init__(self, value):
        self.value = value

    def eval(self):
        return self.value


class Code(BaseBox):
    def __init__(self, message_sends):
        self.message_sends = message_sends


class Message(BaseBox):
    def __init__(self, name):
        self.name = name


class KeywordMessage(BaseBox):
    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters


class BinaryMessage(BaseBox):
    def __init__(self, name, parameter):
        self.name = name
        self.parameter = parameter


class Send(BaseBox):
    def __init__(self, obj, msg):
        self.obj = obj
        self.msg = msg
