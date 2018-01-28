from os import path as opath
from collections import OrderedDict
from enum import Enum
from logging import getLogger as _getLogger

logger = _getLogger('root')


class Sides(Enum):
    CLIENT = "client"
    SERVER = "server"
    BOTH = "both"


class File:
    def __init__(self, name=None, side=Sides.BOTH, hash=None, path=None):
        self.name = name
        self.side = side
        self.hash = hash
        self.path = path

    def __str__(self):
        return "File(name=%(name)s, side=%(side)s%(pathstr)s)" % {"name": self.name, "side": self.side.value, "pathstr": "" if self.path is None else ", path=%s" % self.path}

    def build(self):
        return {"name": self.name, "side": self.side.value, "hash": self.hash}

    def get_files(self, path=None):
        if path is None:
            self.path = self.name
        else:
            self.path = opath.join(path, self.name)
        return self


class Directory:
    def __init__(self, contains=None, name=None, side=Sides.BOTH):
        self.contains = [] if contains is None else contains
        self.name = name
        self.side = side

    def build(self):
        return OrderedDict(name=self.name, type="directory", side=self.side.value, contents=[i.build() for i in self.contains])

    def get_files(self, path=None):
        if path is None:
            path = self.name
        else:
            path = opath.join(path, self.name)
        return [i.get_files(path) for i in self.contains]

    def add(self, f_d_obj, ignore_exists=True):
        if any(x.name == f_d_obj.name for x in self.contains):
            if (not ignore_exists) and (isinstance(f_d_obj, File)):
                raise FileExistsError('File object exists in tree')
            else:
                return next((x for x in self.contains if x.name == f_d_obj.name), None)
        self.contains.append(f_d_obj)
        return f_d_obj

    def __str__(self):
        return "Directory(%s)" % ", ".join([str(i) for i in self.contains])


def build_tree_from_json(jobj):
    if jobj.get("type", "file") == "directory":
        return Directory(contains=[build_tree_from_json(i) for i in jobj["contents"]], name=jobj["name"], side=Sides(jobj["side"]))
    else:
        return File(name=jobj["name"], side=Sides(jobj["side"]), hash=jobj["hash"])


def compare_trees(tree1, tree2):
    """
    :param tree1: the tree you have
    :param tree2: the tree you want
    :return: the stuff to add, the stuff to remove to get the tree you want
    """
    def flatten_list(S):
        if S == []:
            return S
        if isinstance(S[0], list):
            return flatten_list(S[0]) + flatten_list(S[1:])
        return S[:1] + flatten_list(S[1:])

    list1, list2 = flatten_list(tree1.get_files()), flatten_list(tree2.get_files())

    to_add, to_remove = [], []

    for file in list2:
        if not any(x.hash == file.hash for x in list1):
            logger.debug("   ADD %s" % file.path)
            to_add.append(file)

    for file in list1:
        if not any(x.hash == file.hash for x in list2):
            logger.debug("DELETE %s" % file.path)
            to_remove.append(file)

    return to_add, to_remove
