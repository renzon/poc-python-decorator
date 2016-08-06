from mark.decorator import mark


def marked_1():
    print('Marked 1')


marked_1 = mark(marked_1)


@mark
def marked_2():
    print('Marked 1')


def not_marked():
    print('Not Marked')
