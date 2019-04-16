# -*- coding: utf-8 -*-
from collections import OrderedDict

from tinySelf.datastructures.code_generalization import create_copy_with_different_types


class KeyValPair(object):
    def __init__(self, key, val):
        self.key = key
        self.val = val


class Container(object):
    def __init__(self, val):
        self.val = val

    def __eq__(self, other):
        if isinstance(other, Container):
            return self.val == other.val

        return False


class LightWeightDictList(object):
    """
    Implementation with dynamic list used with .append() / .pop().
    """
    def __init__(self):
        self._first_key = None
        self._first_value = None
        self._second_key = None
        self._second_value = None
        self._third_key = None
        self._third_value = None

        self._use_properties = True
        self._use_small_array = False
        self._use_dict = False

        self._max_array_items = 9

        self._dict = None
        self._small_array = None

    def has_key(self, key):
        if self._use_properties:
            return key == self._first_key or key == self._second_key or key == self._third_key
        elif self._use_small_array:
            for kv in self._small_array:
                if kv.key == key:
                    return True
            return False
        else:
            return key in self._dict

    def __contains__(self, key):
        return self.has_key(key)

    def set(self, key, val):
        if self._use_properties:
            if self._first_key is None or self._first_key == key:
                self._first_key = key
                self._first_value = Container(val)
            elif self._second_key is None or self._second_key == key:
                self._second_key = key
                self._second_value = Container(val)
            elif self._third_key is None or self._third_key == key:
                self._third_key = key
                self._third_value = Container(val)
            else:
                self._use_properties = False
                self._use_small_array = True
                self._use_dict = False

                self._small_array = [
                    KeyValPair(self._first_key, self._first_value.val),
                    KeyValPair(self._second_key, self._second_value.val),
                    KeyValPair(self._third_key, self._third_value.val),
                ]

                self._first_key = None
                self._first_value = None
                self._second_key = None
                self._second_value = None
                self._third_key = None
                self._third_value = None

                return self.set(key, val)

        elif self._use_small_array:
            if len(self._small_array) >= self._max_array_items:
                self._use_properties = False
                self._use_small_array = False
                self._use_dict = True

                self._dict = OrderedDict()
                for kv in self._small_array:
                    self._dict[kv.key] = kv.val

                self._small_array = None
                return self.set(key, val)

            for kv in self._small_array:
                if kv.key == key:
                    kv.val = val
                    return

            self._small_array.append(KeyValPair(key, val))

        else:
            self._dict[key] = val

    def __setitem__(self, key, val):
        self.set(key, val)

    def get(self, key, alt=None):
        if self._use_properties:
            if self._first_key == key:
                return self._first_value.val
            elif self._second_key == key:
                return self._second_value.val
            elif self._third_key == key:
                return self._third_value.val
            else:
                return alt
        elif self._use_small_array:
            for kv in self._small_array:
                if kv.key == key:
                    return kv.val

            return alt
        else:
            return self._dict.get(key, alt)

    def __getitem__(self, key):
        if self._use_properties:
            if self._first_key == key:
                return self._first_value.val
            elif self._second_key == key:
                return self._second_value.val
            elif self._third_key == key:
                return self._third_value.val
            else:
                raise KeyError("`%s` not found." % key)
        elif self._use_small_array:
            for kv in self._small_array:
                if kv.key == key:
                    return kv.val

            raise KeyError("`%s` not found." % key)
        else:
            return self._dict[key]

    def delete(self, key):
        if self._use_properties:
            if self._first_key == key:
                self._first_key = self._second_key
                self._second_key = self._third_key
                self._third_key = None

                self._first_value = self._second_value
                self._second_value = self._third_value
                self._third_value = None
            elif self._second_key == key:
                self._second_key = self._third_key
                self._third_key = None

                self._second_value = self._third_value
                self._third_value = None
            elif self._third_key == key:
                self._third_key = None
                self._third_value = None
        elif self._use_small_array:
            for cnt, kv in enumerate(self._small_array):
                if kv.key == key:
                    self._small_array.pop(cnt)
                    return
        else:
            if key in self._dict:
                del self._dict[key]

    def __delitem__(self, key):
        return self.delete(key)

    def keys(self):
        if self._use_properties:
            keys = []
            if self._first_key is not None:
                keys.append(self._first_key)
            if self._second_key is not None:
                keys.append(self._second_key)
            if self._third_key is not None:
                keys.append(self._third_key)

            return keys
        elif self._use_small_array:
            return [kv.key for kv in self._small_array]
        else:
            return self._dict.keys()

    def values(self):
        if self._use_properties:
            values = []
            if self._first_key is not None:
                values.append(self._first_value.val)
            if self._second_key is not None:
                values.append(self._second_value.val)
            if self._third_key is not None:
                values.append(self._third_value.val)

            return values
        elif self._use_small_array:
            return [kv.val for kv in self._small_array]
        else:
            return self._dict.values()

    def __len__(self):
        if self._use_properties:
            length = 0
            if self._first_key is not None:
                length += 1
            if self._second_key is not None:
                length += 1
            if self._third_key is not None:
                length += 1

            return length
        elif self._use_small_array:
            return len(self._small_array)
        else:
            return len(self._dict)

    def copy(self):
        lwd = LightWeightDictList()

        if self._use_properties:
            lwd._first_key = self._first_key
            lwd._first_value = self._first_value
            lwd._second_key = self._second_key
            lwd._second_value = self._second_value
            lwd._third_key = self._third_key
            lwd._third_value = self._third_value
        elif self._use_small_array:
            lwd._small_array = self._small_array
        else:
            lwd._dict = self._dict

        lwd._use_properties = self._use_properties
        lwd._use_small_array = self._use_small_array
        lwd._use_dict = self._use_dict
        lwd._max_array_items = self._max_array_items

        return lwd

    def __eq__(self, other):
        if isinstance(other, LightWeightDictList):
            if self._use_properties and other._use_properties:
                return (self._first_key == other._first_key and
                        self._first_value == other._first_value and
                        self._second_key == other._second_key and
                        self._second_value == other._second_value and
                        self._third_key == other._third_key and
                        self._third_value == other._third_value)
            elif self._use_small_array and other._use_small_array:
                return self._small_array == other._small_array
            elif self._use_dict and other._use_dict:
                return self._dict == other._dict
            else:
                if self.keys() != other.keys():
                    return False

                for key, val in self.iteritems():
                    if other[key] != val:
                        return False

                return True

        elif isinstance(other, dict):
            if self._use_dict:
                return self._dict == other

            other_lwd = LightWeightDict()
            for k, v in other.iteritems():
                other_lwd[k] = v

            return self == other_lwd

        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def iteritems(self):
        if self._use_properties:
            if self._first_key is not None:
                yield self._first_key, self._first_value.val
            if self._second_key is not None:
                yield self._second_key, self._second_value.val
            if self._third_key is not None:
                yield self._third_key, self._third_value.val

        elif self._use_small_array:
            for kv in self._small_array:
                yield kv.key, kv.val

        else:
            for k, v in self._dict.iteritems():
                yield k, v



class LightWeightDict(object):
    """
    Implementation with statically allocated array.
    """
    def __init__(self):
        self._first_key = None
        self._first_value = None
        self._second_key = None
        self._second_value = None
        self._third_key = None
        self._third_value = None

        self._use_properties = True
        self._use_small_array = False
        self._use_dict = False

        self._max_array_items = 9
        self._small_array_len = 0

        self._dict = None
        self._small_array = None

    def has_key(self, key):
        if self._use_properties:
            return key == self._first_key or key == self._second_key or key == self._third_key
        elif self._use_small_array:
            for i in xrange(self._small_array_len):
                if self._small_array[i].key == key:
                    return True
            return False
        else:
            return key in self._dict

    def __contains__(self, key):
        return self.has_key(key)

    def set(self, key, val):
        if self._use_properties:
            if self._first_key is None or self._first_key == key:
                self._first_key = key
                self._first_value = Container(val)
            elif self._second_key is None or self._second_key == key:
                self._second_key = key
                self._second_value = Container(val)
            elif self._third_key is None or self._third_key == key:
                self._third_key = key
                self._third_value = Container(val)
            else:
                self._use_properties = False
                self._use_small_array = True
                self._use_dict = False

                self._small_array = [None for _ in xrange(self._max_array_items)]

                self._small_array[0] = KeyValPair(self._first_key, self._first_value.val)
                self._small_array[1] = KeyValPair(self._second_key, self._second_value.val)
                self._small_array[2] = KeyValPair(self._third_key, self._third_value.val)
                self._small_array[3] = KeyValPair(key, val)
                self._small_array_len = 4

                self._first_key = None
                self._first_value = None
                self._second_key = None
                self._second_value = None
                self._third_key = None
                self._third_value = None

        elif self._use_small_array:
            if self._small_array_len >= self._max_array_items:
                self._use_properties = False
                self._use_small_array = False
                self._use_dict = True

                self._dict = OrderedDict()
                for i in xrange(self._small_array_len):
                    kv = self._small_array[i]
                    self._dict[kv.key] = kv.val

                self._small_array_len = 0
                self._small_array = None

                return self.set(key, val)

            for i in xrange(self._small_array_len):
                kv = self._small_array[i]
                if kv.key == key:
                    kv.val = val
                    return

            self._small_array[self._small_array_len] = KeyValPair(key, val)
            self._small_array_len += 1

        else:
            self._dict[key] = val

    def __setitem__(self, key, val):
        self.set(key, val)

    def get(self, key, alt=None):
        if self._use_properties:
            if self._first_key == key:
                return self._first_value.val
            elif self._second_key == key:
                return self._second_value.val
            elif self._third_key == key:
                return self._third_value.val
            else:
                return alt
        elif self._use_small_array:
            for i in xrange(self._small_array_len):
                kv = self._small_array[i]
                if kv.key == key:
                    return kv.val

            return alt
        else:
            return self._dict.get(key, alt)

    def __getitem__(self, key):
        if self._use_properties:
            if self._first_key == key:
                return self._first_value.val
            elif self._second_key == key:
                return self._second_value.val
            elif self._third_key == key:
                return self._third_value.val
            else:
                raise KeyError("`%s` not found." % key)
        elif self._use_small_array:
            for i in xrange(self._small_array_len):
                kv = self._small_array[i]
                if kv.key == key:
                    return kv.val

            raise KeyError("`%s` not found." % key)
        else:
            return self._dict[key]

    def delete(self, key):
        if self._use_properties:
            if self._first_key == key:
                self._first_key = self._second_key
                self._second_key = self._third_key
                self._third_key = None

                self._first_value = self._second_value
                self._second_value = self._third_value
                self._third_value = None
            elif self._second_key == key:
                self._second_key = self._third_key
                self._third_key = None

                self._second_value = self._third_value
                self._third_value = None
            elif self._third_key == key:
                self._third_key = None
                self._third_value = None

        elif self._use_small_array:
            for i in xrange(self._small_array_len):
                kv = self._small_array[i]

                if kv.key == key:
                    j = i
                    while j < self._small_array_len:
                        self._small_array[j] = self._small_array[j + 1]
                        j += 1
                    self._small_array_len -= 1
                    return

        else:
            if key in self._dict:
                del self._dict[key]

    def __delitem__(self, key):
        return self.delete(key)

    def keys(self):
        if self._use_properties:
            keys = []
            if self._first_key is not None:
                keys.append(self._first_key)
            if self._second_key is not None:
                keys.append(self._second_key)
            if self._third_key is not None:
                keys.append(self._third_key)

            return keys

        elif self._use_small_array:
            return [self._small_array[i].key
                    for i in xrange(self._small_array_len)]

        else:
            return self._dict.keys()

    def values(self):
        if self._use_properties:
            values = []
            if self._first_key is not None:
                values.append(self._first_value.val)
            if self._second_key is not None:
                values.append(self._second_value.val)
            if self._third_key is not None:
                values.append(self._third_value.val)

            return values
        elif self._use_small_array:
            return [self._small_array[i].val
                    for i in xrange(self._small_array_len)]
        else:
            return self._dict.values()

    def __len__(self):
        if self._use_properties:
            length = 0
            if self._first_key is not None:
                length += 1
            if self._second_key is not None:
                length += 1
            if self._third_key is not None:
                length += 1

            return length
        elif self._use_small_array:
            return self._small_array_len
        else:
            return len(self._dict)

    def copy(self):
        lwd = LightWeightDict()

        if self._use_properties:
            lwd._first_key = self._first_key
            lwd._first_value = self._first_value
            lwd._second_key = self._second_key
            lwd._second_value = self._second_value
            lwd._third_key = self._third_key
            lwd._third_value = self._third_value
        elif self._use_small_array:
            lwd._small_array = self._small_array
        else:
            lwd._dict = self._dict

        lwd._use_properties = self._use_properties
        lwd._use_small_array = self._use_small_array
        lwd._use_dict = self._use_dict
        lwd._max_array_items = self._max_array_items
        lwd._small_array_len = self._small_array_len

        return lwd

    def __eq__(self, other):
        if isinstance(other, LightWeightDict):
            if self._use_properties and other._use_properties:
                return (self._first_key == other._first_key and
                        self._first_value == other._first_value and
                        self._second_key == other._second_key and
                        self._second_value == other._second_value and
                        self._third_key == other._third_key and
                        self._third_value == other._third_value)
            elif self._use_small_array and other._use_small_array:
                return (self._small_array_len == other._small_array_len and
                        self._small_array == other._small_array)
            elif self._use_dict and other._use_dict:
                return self._dict == other._dict
            else:
                if self.keys() != other.keys():
                    return False

                for k, v in self.iteritems():
                    if other.get(k) != v:
                        return False

                return True

        elif isinstance(other, dict):
            if self._use_dict:
                return self._dict == other

            other_lwd = LightWeightDict()
            for k, v in other.iteritems():
                other_lwd[k] = v

            return self == other_lwd

        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def iteritems(self):
        if self._use_properties:
            if self._first_key is not None:
                yield self._first_key, self._first_value.val
            if self._second_key is not None:
                yield self._second_key, self._second_value.val
            if self._third_key is not None:
                yield self._third_key, self._third_value.val

        elif self._use_small_array:
            for i in xrange(self._small_array_len):
                kv = self._small_array[i]
                yield kv.key, kv.val

        else:
            for k, v in self._dict.iteritems():
                yield k, v


class LightWeightDictJustProperties(object):
    """
    Implementation with just properties or dict.
    """
    def __init__(self):
        self._first_key = None
        self._first_value = None
        self._second_key = None
        self._second_value = None

        self._use_properties = True
        self._use_dict = False

        self._dict = None

    def has_key(self, key):
        if self._use_properties:
            return key == self._first_key or \
                   key == self._second_key
        else:
            return key in self._dict

    def __contains__(self, key):
        return self.has_key(key)

    def set(self, key, val):
        if self._use_properties:
            if self._first_key is None or self._first_key == key:
                self._first_key = key
                self._first_value = Container(val)
            elif self._second_key is None or self._second_key == key:
                self._second_key = key
                self._second_value = Container(val)
            else:
                self._use_properties = False
                self._use_dict = True
                self._dict = OrderedDict()

                self._dict[self._first_key] = self._first_value.val
                self._dict[self._second_key] = self._second_value.val

                self._first_key = None
                self._first_value = None
                self._second_key = None
                self._second_value = None

                return self.set(key, val)

        else:
            self._dict[key] = val

    def __setitem__(self, key, val):
        self.set(key, val)

    def get(self, key, alt=None):
        if self._use_properties:
            if self._first_key == key:
                return self._first_value.val
            elif self._second_key == key:
                return self._second_value.val
            else:
                return alt
        else:
            return self._dict.get(key, alt)

    def __getitem__(self, key):
        if self._use_properties:
            if self._first_key == key:
                return self._first_value.val
            elif self._second_key == key:
                return self._second_value.val
            else:
                raise KeyError("`%s` not found." % key)
        else:
            return self._dict[key]

    def delete(self, key):
        if self._use_properties:
            if self._first_key == key:
                self._first_key = self._second_key
                self._second_key = None

                self._first_value = self._second_value
                self._second_value = None

            elif self._second_key == key:
                self._second_key = None
                self._second_value = None

        else:
            if key in self._dict:
                del self._dict[key]

    def __delitem__(self, key):
        return self.delete(key)

    def keys(self):
        if self._use_properties:
            keys = []
            if self._first_key is not None:
                keys.append(self._first_key)
            if self._second_key is not None:
                keys.append(self._second_key)

            return keys

        else:
            return self._dict.keys()

    def values(self):
        if self._use_properties:
            values = []
            if self._first_key is not None:
                values.append(self._first_value.val)
            if self._second_key is not None:
                values.append(self._second_value.val)

            return values

        else:
            return self._dict.values()

    def __len__(self):
        if self._use_properties:
            length = 0
            if self._first_key is not None:
                length += 1
            if self._second_key is not None:
                length += 1

            return length

        else:
            return len(self._dict)

    def copy(self):
        lwd = LightWeightDictJustProperties()

        if self._use_properties:
            lwd._first_key = self._first_key
            lwd._first_value = self._first_value
            lwd._second_key = self._second_key
            lwd._second_value = self._second_value
        else:
            lwd._dict = self._dict

        lwd._use_properties = self._use_properties
        lwd._use_dict = self._use_dict

        return lwd

    def __eq__(self, other):
        if isinstance(other, LightWeightDictJustProperties):
            if self._use_properties and other._use_properties:
                return (self._first_key == other._first_key and
                        self._first_value == other._first_value and
                        self._second_key == other._second_key and
                        self._second_value == other._second_value)

            elif self._use_dict and other._use_dict:
                return self._dict == other._dict

            else:
                if self.keys() != other.keys():
                    return False

                for k, v in self.iteritems():
                    if other.get(k) != v:
                        return False

                return True

        elif isinstance(other, dict):
            if self._use_dict:
                return self._dict == other

            other_lwd = LightWeightDictJustProperties()
            for k, v in other.iteritems():
                other_lwd[k] = v

            return self == other_lwd

        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def iteritems(self):
        if self._use_properties:
            if self._first_key is not None:
                yield self._first_key, self._first_value.val
            if self._second_key is not None:
                yield self._second_key, self._second_value.val

        else:
            for k, v in self._dict.iteritems():
                yield k, v



class LightWeightDictObjects(LightWeightDict):
    """Just token for IDE rewritten in create_copy_with_different_types()"""


exec create_copy_with_different_types(Container, "ObjectContainer")
exec create_copy_with_different_types(KeyValPair, "KeyValPairObject")
exec create_copy_with_different_types(LightWeightDict, "LightWeightDictObjects",
                                      [["Container", "ObjectContainer"],
                                       ["KeyValPair", "KeyValPairObject"]])
