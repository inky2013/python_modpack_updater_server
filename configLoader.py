import json
import fileHelper
from os.path import join as join_path
from pathlib import Path
import dictionaryHelper


class Struct:
    def __init__(self, d):
        for k in d:
            if isinstance(d[k], dict):
                self.__dict__[k] = Struct(d[k])
            else:
                self.__dict__[k] = d[k]


class JSONFormat:
    @staticmethod
    def save(d):
        return json.dumps(d, indent=4)

    @staticmethod
    def load(text):
        return json.loads(text)


class PropertiesFormat:
    @staticmethod
    def save(d):
        return "\n".join(["%s=%s" % (k, d[k]) for k in d])

    @staticmethod
    def load(text):
        return dict(line.strip().split('=') for line in text.split("\n") if not line.strip().startswith('#'))


class ListFormat:
    @staticmethod
    def save(lst):
        return "\n".join(lst)

    @staticmethod
    def load(text):
        return [i for i in text.split("\n") if i != ""]


def get_configuration(file, default=None, fmt=JSONFormat, update_config_file=True):
    try:
        loaded = fmt.load(fileHelper.readFile(file))
    except FileNotFoundError:
        loaded = {}
    if default is None: default = {}
    loaded = dictionaryHelper.recursive_update(default, loaded)
    if update_config_file:
        save_configuration(file, loaded, fmt)

    return loaded


def save_configuration(file, value, fmt=JSONFormat):
    parts = Path(file).parts[:-1]
    if len(parts) != 0: fileHelper.ensureDirectory(join_path(*parts))
    fileHelper.writeFile(file, fmt.save(value))


def get_list(file, default=None, fmt=ListFormat, update_list_file=True, extend_populated_list=False):
    try:
        loaded = fmt.load(fileHelper.readFile(file))
    except FileNotFoundError:
        loaded = []
    if default is None: default = []
    if len(loaded) == 0 or extend_populated_list:
        loaded.extend(default)
    if update_list_file:
        save_list(file, loaded, fmt)

    return loaded


def save_list(file, value, fmt=ListFormat):
    parts = Path(file).parts[:-1]
    if len(parts) != 0: fileHelper.ensureDirectory(join_path(*parts))
    fileHelper.writeFile(file, fmt.save(value))


def get_global_config():
    return Struct(get_configuration(
        "config.json",
        {
            "fileDir": "files",
            "packDir": "packs",
            "patterns": "patterns.txt",
            "fileIndex": "file-index.properties",
            "logLevel": "DEBUG"
        }))