

class MultiKeyData(object):

    def __init__(self):
        self._keys = {}
        self._values = {}
        self._links = {}
        self._index = 0

    def __add_item(self, key, value):
        if key not in self._keys:
            self._keys[key] = self._index
            self._values[self._index] = value
            self._links[self._index] = 1
            return 1
        else:
            self._values[self._keys[key]] = value
            return 0

    def multi_set(self, keys, value):
        count = 0
        for key in keys:
            count += self.__add_item(key, value)

        if count>0:
            self._links[self._index] += count-1
            self._index += 1

    def get_values(self):
        return list(self._values.values())

    def get_keys(self):
        return list(self._keys.keys())

    def __getitem__(self, key):
        return self._values[self._keys[key]] if key in self._keys else None

    def __setitem__(self, key, value):
        self._index += self.__add_item(key, value)

    def __delitem__(self, key):
        index = self._keys[key]
        self._links[index] += -1
        del self._keys[key]
        if self._links[index]==0:
            del self._links[index]
            del self._values[index]

    def __str__(self):
        return f'keys: {self._keys}\n' \
               f'values: {self._values}\n' \
               f'links: {self._links}'


if __name__ == '__main__':
    print('MultiKeuData Test')
    data = MultiKeyData()
    data['a'] = 101
    data['b'] = 201
    print("data['b']: ", data['b'])

    print('-------------')
    print('data: ')
    print(data)

    print('-------------')
    data.multi_set(('a', 'b', 'c', 'd'), 'hello, world!')
    print(data)

    print('-------------')
    data.multi_set(('a', 'b', 'c', 'd'), 'hello, world!')
    print(data)

    print('-------------')
    data.multi_set(('a', 'b', 'c', 'd', 'e'), 'hello, world!')
    print(data)

    print('-------------')
    del data['e']
    print(data)

    print('-------------')
    print('keys: ', data.get_keys())
    print('values: ', data.get_values())
