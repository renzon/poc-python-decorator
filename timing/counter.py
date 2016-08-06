from timing.timer import timing


@timing
def count():
    for i in range(1000):
        print(i)


if __name__ == '__main__':
    count()
    print(count.__name__)
