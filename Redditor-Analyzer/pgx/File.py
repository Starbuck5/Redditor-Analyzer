import os
import json
import pickle
import codecs

from pgx import handle_path

# helper class to deal with files
# File is a list-like object, where each list index is a line of the file
# writes numbers, strings, lists, and dicts to file using JSON - they are human readable and easily editable
# any other object is encoded using pickle, compressed into base64, and stored
# USAGE EXAMPLE:
#
# file = File("test.txt")
#
# line1 = file[0] #gets the first line of the file (assuming there are things there)
#
# file[0] = [1, 2, "yes"] #sets the first line of the file to this list
#
# file[1] = MyClass(15, 9) #sets the 2nd line of the file to any object
#
# file[0,2] = "no" #turns the 3rd element of the 1st line, formerly "yes", to "no"
#
# file[0][2] = "no" #does the same as thing previous operation
# file.sync()       #do whichever one you prefer
#
# var = file[0,0] #getting items also supports the tuple-esque notation, although it isn't necessary
#
# var = file[0][0] #this does the operation just as well
#
# also has a bunch of other more methods that are much more self explanatory
#
class File:
    # supports text-writable files - like .txt or .json
    def __init__(self, filepath):
        self.path = handle_path(filepath)
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"No file at {filepath}")
        with open(self.path, "r") as opened_file:
            self.data = [0 for i in range(len(opened_file.readlines()))]
        self._update_all_data()

    # version of init for files that don't yet exist
    @staticmethod
    def create(path):
        fixed_path = handle_path(path)
        file = open(fixed_path, "x")
        file.close()
        return File(path)

    # supposed to wipe file
    def clear(self):
        with open(self.path, "w") as opened_file:
            opened_file.truncate(0)
        self.data.clear()

    # deletes the file and all data associated with it
    def delete(self):
        os.remove(self.path)
        self.data = []

    # manual way of updating file with changes
    def sync(self):
        self._update_all_file()

    # called internally to completely regenerate self.data from the file
    def _update_all_data(self):
        i = 0
        while True:
            try:
                self._update_data(i)
            except:
                break
            i += 1

    # updates one index of self.data from the file
    def _update_data(self, key):
        with open(self.path, "r") as opened_file:
            item = opened_file.readlines()[key]
        item = self._decode(item)
        self.data[key] = item

    # decodes a line of the file back into it's object
    def _decode(self, string):
        try:
            return json.loads(string)
        except:
            pass
        try:  # if json can't load it, how about pickle?
            return pickle.loads(codecs.decode(string.encode(), "base64"))
        except:
            return "undecodable object"

    # called internally to completely regenerate the file from self.data
    def _update_all_file(self):
        i = 0
        while True:
            try:
                self._update_file(i)
            except:
                break
            i += 1

    # updates one line of the file from it's corresponding self.data index
    def _update_file(self, key):
        write_string = self._encode(self.data[key])
        addendum = "" if key == len(self.data) - 1 else "\n"
        write_string += addendum
        with open(self.path, "r+") as opened_file:
            contents = opened_file.readlines()
            if addendum == "":  # strips out anything beyond the last line
                contents = contents[: key + 1]

            try:  # this try/except puts the write string into the contents list
                contents[key] = write_string
            # if the length has been increased, this except statement handles it
            # it assumes the _update_file is being called in order of low to high, and it should be
            except:
                contents.append(write_string)

            opened_file.truncate(key)
            opened_file.seek(0)
            opened_file.writelines(contents)

    # takes a python object and turns into a string for the file
    def _encode(self, obj):
        # print(f"encoding {obj} for file write")
        try:  # tries to encode using json format
            return json.dumps(obj)
        except:  # if it can't, it uses pickle
            # subsequent one-liner is the product of much trial and error
            return str(codecs.encode(pickle.dumps(obj), "base64").decode())

    # overrides file[index]
    def __getitem__(self, key):
        try:
            _, _ = key
            return self._deep_getitem(key)
        except:
            # print(f"GET - key: {key}")
            self._update_data(key)
            return self.data[key]

    # for file[index1,index2]
    def _deep_getitem(self, key):
        # print(f"DEEPGET - key: {key}")
        return self.data[key[0]][key[1]]

    # overrides file[index] = thing
    def __setitem__(self, key, value):
        try:
            _, _ = key
            self._deep_setitem(key, value)
        except:
            # print(f"SET - key: {key}, value: {value}")
            self.data[key] = value
            self._update_file(key)

    # for file[index1, index2] = thing
    def _deep_setitem(self, key, value):
        # print(f"DEEPSET - key: {key}, value: {value}")
        self.data[key[0]][key[1]] = value
        self._update_file(key[0])

    # ya know, the string thing
    def __str__(self):
        self._update_all_data()
        string = f"--{self.path}--\n"
        datas = [str(i) for i in self.data]
        string += "\n".join(datas)
        return string

    # not sure how useful this one will be, but it overrides ==
    def __eq__(self, other):
        return self.path == other.path

    # for the for/each loops and 'in' keyword
    def __iter__(self):
        self._update_all_data()
        return self.data

    # overrides len(file), for those for loops!
    def __len__(self):
        return len(self.data)

    # "+="
    def __iadd__(self, other):
        self.data += other
        self._update_all_file()
        return self

    # ya know, like a list
    def append(self, other):
        self.data.append(other)
        self._update_all_file()
