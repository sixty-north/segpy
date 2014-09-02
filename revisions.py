SEGY_REVISION_0 = 0
SEGY_REVISION_1 = 1

VARIANTS = {SEGY_REVISION_0: SEGY_REVISION_0,
            SEGY_REVISION_1: SEGY_REVISION_1,
            0: SEGY_REVISION_0,
            1: SEGY_REVISION_1,
            100: SEGY_REVISION_1,
            256: SEGY_REVISION_1}


class SegYRevisionError(Exception):
    pass


def canonicalize_revision(revision):
    """Canonicalize a SEG Y revision.

    Various SEG Y revisions are seen in the wild; this function canonicalizes the supplies revision
    to either SEGY_REVISION_0 or SEGY_REVISION_1.

    Args:
        revision: Any object representing a SEG Y revision.

    Returns:
        Either SEGY_REVISION_0 or SEGY_REVISION_1.

    Raises:
        SegYRevisionError: If the revision is not known.
    """
    try:
        return VARIANTS[revision]
    except KeyError:
        raise SegYRevisionError("Unknown SEG Y Revision {!r}".format(revision))
