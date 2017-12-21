from collections import deque

from hypothesis import given, assume
from hypothesis.strategies import data, integers
from pytest import raises

from segpy.reversed_sequence_view import ReversedSequenceView
from test.predicates import check_balanced
from test.strategies import sequences


@given(seq=sequences())
def test_contains(seq):
    rev = ReversedSequenceView(seq)
    assert all(item in rev for item in seq)


@given(seq=sequences())
def test_length(seq):
    rev = ReversedSequenceView(seq)
    assert len(rev) == len(seq)


@given(seq=sequences())
def test_iteration(seq):
    rev = ReversedSequenceView(seq)
    assert all(a == b for a, b in zip(rev, reversed(seq)))


@given(seq=sequences())
def test_get_item(seq):
    rev = ReversedSequenceView(seq)
    assert all(rev[i] == b for i, b in enumerate(reversed(seq)))


@given(seq=sequences())
def test_count(seq):
    rev = ReversedSequenceView(seq)
    assert all(seq.count(a) == rev.count(a) for a in seq)


@given(seq=sequences())
def test_reversed(seq):
    rev = ReversedSequenceView(seq)
    assert all(a == b for a, b in zip(seq, reversed(rev)))


@given(seq=sequences())
def test_index(seq):
    rev = ReversedSequenceView(seq)
    assert all(rev.index(a) == list(reversed(seq)).index(a) for a in seq)


@given(seq=sequences(elements=integers()), data=data())
def test_index_not_found_raises_value_error(seq, data):
    missing = data.draw(integers())
    assume(missing not in seq)
    rev = ReversedSequenceView(seq)
    with raises(ValueError):
        rev.index(missing)


@given(seq=sequences())
def test_positive_out_of_range_indexes_raise_value_error(seq):
    rev = ReversedSequenceView(seq)
    with raises(IndexError):
        _ = rev[len(rev)]


@given(seq=sequences())
def test_negative_indexing(seq):
    rev = ReversedSequenceView(seq)
    assert all(rev[index] == a for index, a in zip(range(-1, -len(seq), -1), seq))


@given(seq=sequences())
def test_negative_out_of_range_indexes_raise_value_error(seq):
    rev = ReversedSequenceView(seq)
    with raises(IndexError):
        _ = rev[-len(rev) - 1]


@given(seq=sequences())
def test_repr(seq):
    rev = ReversedSequenceView(seq)
    r = repr(rev)
    assert r.startswith('ReversedSequenceView')
    assert check_balanced(r)
