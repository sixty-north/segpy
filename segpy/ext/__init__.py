import pkg_resources

loaded = set()


def load_entry_points(name=None):
    """Load extension packages into the segpy.ext namespace.

    Any packages registered against the 'segpy.ext' entry-point group will be
    installed dynamically into the segpy.ext namespace.
    """
    for entry_point in pkg_resources.iter_entry_points(group='segpy.ext', name=name):
        package = entry_point.load()
        if package not in loaded:
            loaded.add(package)
            __path__.extend(package.__path__)
            package.load()


load_entry_points()
