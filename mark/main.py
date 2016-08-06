from mark import decorator
# Need only be imported to mark functions/methods
from mark import marked

if __name__ == '__main__':
    for f in decorator._marked:
        print(f.__name__)

    # Original functions are the same:
    marked.marked_1()
    marked.marked_2()
    marked.not_marked()
