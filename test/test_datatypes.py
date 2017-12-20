from hypothesis import given, assume
from hypothesis.strategies import sampled_from, text
from pytest import raises

from segpy.datatypes import size_in_bytes

LEGAL_CTYPES = ['I', 'i', 'h', 'H', 'b', 'B', 'f', 'ibm']


@given(ctype=sampled_from("Ii"))
def test_integers_are_four_bytes(ctype):
    assert size_in_bytes(ctype) == 4


@given(ctype=sampled_from("Hh"))
def test_shorts_are_two_bytes(ctype):
    assert size_in_bytes(ctype) == 2


@given(ctype=sampled_from("Bb"))
def test_bytes_are_one_byte(ctype):
    assert size_in_bytes(ctype) == 1


@given(ctype=sampled_from(['f', 'ibm']))
def test_floats_are_four_bytes(ctype):
    assert size_in_bytes(ctype) == 4


@given(ctype=text())
def test_illegal_ctypes_raise_value_error(ctype):
    assume(ctype not in LEGAL_CTYPES)
    with raises(ValueError):
        size_in_bytes(ctype)
