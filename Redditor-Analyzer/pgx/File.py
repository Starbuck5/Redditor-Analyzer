import os
import json
import codecs
import pickle

from pgx import path


class WrappedSequence:
    """An object that calls a function every time its data is modified

    Can be constructed out of a tuple, list, or dictionary - probably
    other things too, but those have all operations mapped.
    """

    def __init__(self, data, callback):
        self.data = data
        self.callback = callback

    def get_data(self):
        try:
            return self.data.copy()
        except AttributeError:
            return self.data

    def set_data(self, data):
        self.data = data
        self.callback(self.data)

    def __repr__(self):
        return f"<WrappedSequence({self.data}, {self.callback})>"

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __eq__(self, other):
        return self.data == other

    def __lt__(self, other):
        return self.data < other

    def __getitem__(self, key):
        """ List/Dict/Tuple operation """
        item = self.data[key]
        if hasattr(type(item), "__iter__"):
            item = WrappedSequence(item, self.callback)
        return item

    def __setitem__(self, key, value):
        """ List/Dict operation """
        self.data[key] = value
        self.callback(self.data)

    def __delitem__(self, key):
        """ List/Dict operation """
        del self.data[key]
        self.callback(self.data)

    def __mul__(self, other):
        """ List/Tuple operation """
        return WrappedSequence(self.get_data() * other, self.callback)

    __rmul__ = __mul__

    def __imul__(self, other):
        """ List/Tuple operation """
        self.data *= other
        self.callback(self.data)
        return self

    def __add__(self, other):
        """ List/Tuple operation """
        return WrappedSequence(self.get_data() + other, self.callback)

    def __iadd__(self, other):
        """ List/Tuple operation """
        self.data += other
        self.callback(self.data)
        return self

    def pop(self, *args):
        """ List/Dict operation """
        self.data.pop(*args)
        self.callback(self.data)

    def append(self, other):
        """ List operation """
        self.data.append(other)
        self.callback(self.data)

    def reverse(self):
        """ List operation """
        self.data.reverse()
        self.callback(self.data)

    def clear(self):
        """ List/Dict operation"""
        self.data.clear()
        self.callback(self.data)

    def sort(self, *args):
        """ List operation """
        self.data.sort(*args)
        self.callback(self.data)

    def setdefault(self, *args):
        """ Dict operation """
        self.data.setdefault(*args)

    def popitem(self):
        """ Dict operation """
        item = self.data.popitem()
        self.callback(self.data)
        return item

    def remove(self, value):
        """ List operation """
        self.data.remove(value)
        self.callback(self.data)

    def insert(self, position, value):
        """ List operation """
        self.data.insert(position, value)
        self.callback(self.data)

    def get(self, *args):
        """ Dict operation """
        return self.data.get(*args)

    def count(self, value):
        """ List/Tuple operation """
        return self.data.count(value)

    def index(self, value):
        """ List/Tuple operation """
        return self.data.index(value)

    def extend(self, iterable):
        """ List operation """
        self.data.extend(iterable)
        self.callback(self.data)

    def update(self, other):
        """ Dict operation """
        self.data.update(other)
        self.callback(self.data)

    def keys(self):
        """ Dict operation """
        return self.data.keys()

    def values(self):
        """ Dict operation """
        return self.data.values()

    def items(self):
        """ Dict operation """
        return self.data.items()

    def copy(self):
        """ List/Dict/Tuple operation """
        return WrappedSequence(self.get_data(), self.callback)


def _rewrite_callback(data, pgxfile):
    pgxfile._sync()


def _create_callback(pgxfile):
    return lambda x: _rewrite_callback(x, pgxfile)


class File(WrappedSequence):
    def __init__(self, filepath):
        self.filepath = path.handle(filepath)

        lines = []
        with open(self.filepath) as file:
            lines = file.readlines()

        data = []
        for line in lines:
            try:  # load line through JSON
                data.append(json.loads(line))
            except json.decoder.JSONDecodeError:  # load line through base64 pickle
                data.append(pickle.loads(codecs.decode(line.encode(), "base64")))

        super().__init__(data, _create_callback(self))

    @staticmethod
    def create(filepath, data=[]):
        """ Make a pgx.File object out of a file that doesn't exist yet """
        filepath = path.handle(filepath)

        tmp = lambda: None
        tmp.filepath = filepath
        tmp.data = data
        File._sync(tmp)

        return File(filepath)

    def delete(self):
        """ Remove the pgx.File object's corresponding file and all data """
        print("what")
        os.remove(self.filepath)
        self.data.clear()

    def _sync(self):
        lines = []
        for data in self.data:
            try:  # save line through JSON
                lines.append(json.dumps(data) + "\n")
            except TypeError:  # save line through base64 pickle
                lines.append(codecs.encode(pickle.dumps(data), "base64").decode())

        with open(self.filepath, "w") as file:
            file.writelines(lines)

    def __repr__(self):
        return f"<FileObject({self.data})>"
