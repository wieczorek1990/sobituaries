import random
import string


def random_ascii_lowercase(length=4):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def access_mutable(request, callback):
    mutable = request.data._mutable
    request.data._mutable = True
    callback()
    request.data._mutable = mutable
