"""SEG Y Revision numbers

From the specification:

    SEG Y Format Revision Number. This is a 16-bit unsigned value with a Q- point between the first and second bytes.
    Thus for SEG Y Revision 1.0, as defined in this document, this will be recorded as 0100 in base 16.
"""


SEGY_REVISION_0 = 0x0000
SEGY_REVISION_1 = 0x0100

VARIANTS = {
    SEGY_REVISION_0: SEGY_REVISION_0,  # Ensure that SEGY_REVISION_0 maps to itself
    SEGY_REVISION_1: SEGY_REVISION_1,  # Ensure that SEGY_REVISION_1 maps to itself
    1: SEGY_REVISION_1,                # Common, but erroneous, decimal one
    100: SEGY_REVISION_1}              # Common, but erroneous, decimal one-hundred


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
