def functions(arg, *args, **kwargs):
    print(type(arg))
    print(arg)
    print(type(args))
    print(args)
    print(type(kwargs))
    print(kwargs)


if __name__ == '__main__':
    functions("test", "q", "w", "e", a="a", b="b")
