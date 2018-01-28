import hashlib


def _read_chunks(file_handle, chunk_size=8192):
    while True:
        data = file_handle.read(chunk_size)
        if not data:
            break
        yield data


def md5(file_handle):
    hasher = hashlib.md5()
    for chunk in _read_chunks(file_handle):
        hasher.update(chunk)
    return hasher.hexdigest()