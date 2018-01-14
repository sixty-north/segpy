"""SEG Y Revision numbers

From the specification:

    SEG Y Format Revision Number. This is a 16-bit unsigned value with a Q- point between the first and second bytes.
    Thus for SEG Y Revision 1.0, as defined in this document, this will be recorded as 0100 in base 16.
"""

# It's not at all obvious to me whether this means 0xHH.LL where the value is in binary-coded decimal, (in which case
# version 1.1 would be represented as 0x0101, or whether it is in fixed-point binary, in which case we can't represent
# version 1.1.  Until I learn otherwise, I'm going for the BCD interpretation.


from decimal import Decimal
from enum import IntEnum


class SegYRevision(IntEnum):
    REVISION_0 = 0x0000
    REVISION_1 = 0x0100


VARIANTS = {
    SegYRevision.REVISION_0: SegYRevision.REVISION_0,  # Ensure that SEGY_REVISION_0 maps to itself
    SegYRevision.REVISION_1: SegYRevision.REVISION_1,  # Ensure that SEGY_REVISION_1 maps to itself
    1: SegYRevision.REVISION_1,                # Common, but erroneous, decimal one
    100: SegYRevision.REVISION_1}              # Common, but erroneous, decimal one-hundred


class SegYRevisionError(Exception):
    pass


def canonicalize_revision(revision):
    """Canonicalize a SEG Y revision.

    Various SEG Y revisions are seen in the wild; this function canonicalizes the supplies revision
    to either SegYRevision.REVISION_0 or SegYRevision.REVISION_1.

    Args:
        revision: Any object representing a SEG Y revision.

    Returns:
        An integer revision - either SegYRevision.REVISION_0 or SegYRevision.REVISION_1.

    Raises:
        SegYRevisionError: If the revision is not known.
    """
    try:
        return VARIANTS[revision]
    except KeyError:
        raise SegYRevisionError("Unknown SEG Y Revision raw={!r} hex={} decimal={}".format(
            revision, hex(revision), integer_to_decimal_revision(revision)))


def integer_to_decimal_revision(revision):
    """Convert a SEG Y revision integer into decimal form.

    Args:
        revision: An canonical revision integer e.g. as produced by
            a call to canonicalize_revision().

    Returns:
        A decimal real number.
    """
    lo = revision & 0xFF
    hi = (revision >> 8) & 0xFF
    return Decimal(hi) + Decimal(lo)/Decimal(10)
