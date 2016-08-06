from functools import wraps
from time import clock


def timing(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        begin = clock()
        ret = func(*args, **kwargs)
        elapsed = clock() - begin
        elapsed * 1000  # transforming im ms
        print("Function %s executed in %s ms" % (func.__name__, elapsed))
        return ret

    return wrapper
