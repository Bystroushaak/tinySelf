# -*- coding: utf-8 -*-


class LightWeightDict(object):
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

        self._max_array_items = 8

        self._dict = None
        self._small_array = None

    def has_key(self, key):
        if self._use_properties:
            return key == self._first_key or key == self._second_key or key == self._third_key
        elif self._use_small_array:
            for k, _ in self._small_array:
                if key == k:
                    return True
            return False
        else:
            return key in self._dict

    def set(self, key, val):
        if self._use_properties:
            if self._first_key is None or self._first_key == key:
                self._first_key = key
                self._first_value = val
            elif self._second_key is None or self._second_key == key:
                self._second_key = key
                self._second_value = val
            elif self._third_key is None or self._third_key == key:
                self._third_key = key
                self._third_value = val
            else:
                self._use_properties = False
                self._use_small_array = True
                self._use_dict = False

                self._small_array = [
                    [self._first_key, self._first_value],
                    [self._second_key, self._second_value],
                    [self._third_key, self._third_value],
                ]

                self._first_key = None
                self._first_value = None
                self._second_key = None
                self._second_value = None
                self._third_key = None
                self._third_value = None

                return self.set(key, val)

        elif self._use_small_array:
            if len(self._small_array) >= 8:
                self._use_properties = False
                self._use_small_array = False
                self._use_dict = True

                self._dict = {
                    k: v
                    for k, v in self._small_array
                }
                self._small_array = None
                return self.set(key, val)

            for cnt, kv in enumerate(self._small_array):
                k = kv[0]
                if k == key:
                    kv[1] = val
                    return

            self._small_array.append([key, val])

        else:
            self._dict[key] = val

    def get(self, key, alt=None):
        if self._use_properties:
            if self._first_key == key:
                return self._first_value
            elif self._second_key == key:
                return self._second_value
            elif self._third_key == key:
                return self._third_value
            else:
                return alt
        elif self._use_small_array:
            for k, v in self._small_array:
                if k == key:
                    return v

            return alt
        else:
            return self._dict.get(key, alt)

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
                k = kv[0]
                if k == key:
                    self._small_array.pop(cnt)
                    return
        else:
            if key in self._dict:
                del self._dict[key]

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
            return [kv[0] for kv in self._small_array]
        else:
            return self._dict.keys()

    def values(self):
        if self._use_properties:
            values = []
            if self._first_value is not None:
                values.append(self._first_value)
            if self._second_value is not None:
                values.append(self._second_value)
            if self._third_value is not None:
                values.append(self._third_value)

            return values
        elif self._use_small_array:
            return [kv[1] for kv in self._small_array]
        else:
            return self._dict.values()
