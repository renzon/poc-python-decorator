_marked = []


def mark(func):
    _marked.append(func)
    return func
