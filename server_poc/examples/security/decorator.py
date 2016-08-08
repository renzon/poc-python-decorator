from functools import wraps


def restricted_to(*groups):
    allowed_groups = set(groups)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'group' not in kwargs and len(args) == 0:
                print('No defined group')
                return
            group = kwargs['group'] if 'group' in kwargs else args[0]
            if group in allowed_groups:
                func(*args, **kwargs)
            else:
                print('Group %s cant access this path' % group)

        return wrapper

    return decorator
