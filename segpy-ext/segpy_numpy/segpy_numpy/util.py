from segpy.util import make_sorted_distinct_sequence


def is_range_superset_of_range(superset_range, subset_range):
    """Are all the elements of subset_range elements of superset_range?
    """
    if subset_range.start not in superset_range:
        return False
    if subset_range.step % superset_range.step != 0:
        return False
    if subset_range[-1] > superset_range[-1]:
        return False
    assert set(subset_range).issubset(set(superset_range))
    return True


def is_superset(superset, subset):
    """A more general version of set.issuperset that is smart enough to work with ranges."""
    if isinstance(subset, range) and isinstance(superset, range):
        return is_range_superset_of_range(superset, subset)
    if isinstance(superset, range):
        return all(item in superset for item in subset)
    if isinstance(superset, set):
        return superset.issuperset(subset)
    if isinstance(subset, set):
        return subset.issubset(superset)
    return set(superset).issuperset(subset)


def ensure_superset(superset, subset):
    """Ensure that one collection is a subset of another.

    Args:
        superset: A sequence containing all items.

        subset: Subset must either be a collection the elements of which are a subset of
            superset, or a slice object, in which case the subset items will be sliced
            from superset.
    Returns:
        A sorted, distinct collection which is a subset of superset.

    Raises:
        ValueError: If the items in subset are not a subset of the items in all_items.
    """
    if subset is None:
        return superset
    elif isinstance(subset, slice):
        return superset[subset]
    else:
        subset = make_sorted_distinct_sequence(subset)
        if not is_superset(superset, subset):
            raise ValueError("subset_or_slice {!r} is not a subset of all_items {!r}"
                             .format(subset, superset))
        return subset
