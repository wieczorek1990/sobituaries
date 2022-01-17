import random
import string


def random_ascii_lowercase(length=4):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))
