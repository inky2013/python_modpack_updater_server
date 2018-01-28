from os import path as opath
from os import makedirs

def readFile(path, mode="r"):
    with open(path, mode) as f:
        return f.read()

def writeFile(path, data, mode="w+"):
    with open(path, mode) as f:
        f.seek(0)
        f.write(data)

def readFileDefaults(path, mode="r", default=""):
    try:
        return readFile(path, mode)
    except IOError:
        return default

def file_exists(path): return opath.exists(path) and opath.isfile(path)
def dir_exists(path): return opath.exists(path) and opath.isdir(path)


def ensureDirectory(dir):
    if not opath.exists(dir):
        makedirs(dir)


def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


