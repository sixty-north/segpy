from hypothesis import given, assume
from hypothesis.strategies import integers
from pytest import raises

from segpy.revisions import canonicalize_revision, SegYRevision, SegYRevisionError


class TestCanonicalizeRevision:

    def test_correct_revision_zero(self):
        assert canonicalize_revision(0x0000) == SegYRevision.REVISION_0

    def test_correct_revision_one(self):
        assert canonicalize_revision(0x0100) == SegYRevision.REVISION_1

    def test_correct_revision_one_from_integer_one(self):
        assert canonicalize_revision(1) == SegYRevision.REVISION_1

    def test_correct_revision_one_from_integer_one_hundred(self):
        assert canonicalize_revision(100) == SegYRevision.REVISION_1

    @given(r=integers())
    def test_incorrect_revision_raises_segy_revision_error(self, r):
        assume(r not in {0x0000, 0x0100, 1, 100})
        with raises(SegYRevisionError):
            canonicalize_revision(r)

