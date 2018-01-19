from enum import IntEnum

from hypothesis import given
from hypothesis.strategies import integers, one_of
from pytest import raises

from segpy.field_types import Int16, NNInt16, Int32, NNInt32, IntEnumFieldMeta


@given(n=integers(min_value=-32768, max_value=32767))
def test_int16_in_range_is_equal_to_int(n):
    assert Int16(n) == n


@given(n=one_of(integers(max_value=-32769),
                integers(min_value=32768)))
def test_int16_out_of_range_raises_value_error(n):
    with raises(ValueError):
        Int16(n)


@given(n=integers(min_value=0, max_value=32767))
def test_nnint16_in_range_is_equal_to_int(n):
    assert NNInt16(n) == n


@given(n=one_of(integers(max_value=-1),
                integers(min_value=32768)))
def test_nnint16_out_of_range_raises_value_error(n):
    with raises(ValueError):
        NNInt16(n)


@given(n=integers(min_value=-2147483648, max_value=2147483647))
def test_int32_in_range_is_equal_to_int(n):
    assert Int32(n) == n


@given(n=one_of(integers(max_value=-2147483649),
                integers(min_value=2147483648)))
def test_int32_out_of_range_raises_value_error(n):
    with raises(ValueError):
        Int32(n)


@given(n=integers(min_value=0, max_value=2147483647))
def test_nnint32_in_range_is_equal_to_int(n):
    assert NNInt32(n) == n


@given(n=one_of(integers(max_value=-1),
                integers(min_value=2147483648)))
def test_nnint32_out_of_range_raises_value_error(n):
    with raises(ValueError):
        NNInt32(n)


@given(p=integers(min_value=-32768, max_value=32767),
       q=integers(min_value=-32768, max_value=32767))
def test_int_enum_field_meta_in_range(p, q):

    class ExampleEnum(IntEnum):
        MINIMUM_ITEM = p
        MAXIMUM_ITEM = q

    class TraceSortingField(metaclass=IntEnumFieldMeta,
                            enum=ExampleEnum):
        pass


@given(p=one_of(integers(max_value=-32769),
                integers(min_value=32768)),
       q=one_of(integers(max_value=-32769),
                integers(min_value=32768)))
def test_int_enum_field_meta_out_of_range_raises_value_error(p, q):

    class ExampleEnum(IntEnum):
        MINIMUM_ITEM = p
        MAXIMUM_ITEM = q

    with raises(ValueError):
        class TraceSortingField(metaclass=IntEnumFieldMeta,
                                enum=ExampleEnum):
            pass
