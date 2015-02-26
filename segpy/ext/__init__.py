import pkg_resources

loaded = set()


def load_entry_points(name=None):
    for entry_point in pkg_resources.iter_entry_points(group='segpy.ext', name=name):
        package = entry_point.load()
        if package not in loaded:
            loaded.add(package)
            __path__.extend(package.__path__)
            package.load()


load_entry_points()
