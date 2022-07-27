def all_subclasses(cls):
    for subcls in cls.__subclasses__():
        yield from all_subclasses(subcls)
        yield subcls
