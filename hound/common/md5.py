import hashlib


def getMd5(item):
    return str(hashlib.md5(item).hexdigest())

