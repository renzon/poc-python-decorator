from mark import decorator
if __name__ == '__main__':
    # Need only be imported to mark functions/methods
    from mark import marked
    for f in decorator._marked:
        print(f.__name__)