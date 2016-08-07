_routes = {}


def route(*paths):
    def decorator(func):
        for p in paths:
            _routes[p] = func
        return func

    return decorator


def execute(path, *args, **kwargs):
    print('Receiving Request on path: %s' % path)
    if path not in _routes:
        print('404 page not Found')
        return
    _routes[path](*args, **kwargs)
