import inspect
import pickle

from copy import copy

from pytest import raises
from hypothesis import given, assume
from hypothesis.strategies import integers

from segpy.header import field, Header, are_equal
from segpy.field_types import Int32, NNInt32
from segpy.datatypes import LIMITS, SegYType

from test.predicates import check_balanced


class ExampleHeader(Header):

    field_a = field(
        Int32, offset=1, default=0, documentation=
        """Field A. This is field A.""")

    field_b = field(
        NNInt32, offset=5, default=42, documentation=
        "Field B. This is field B.")

    field_c = field(
        Int32, offset=9, default=-1, documentation=
        "Field C. This is field C.")


class TestHeader:

    def test_initialize_with_defaults(self):
        h = ExampleHeader()
        assert h.field_a == 0
        assert h.field_b == 42
        assert h.field_c == -1

    def test_initialize_with_positional_arguments(self):
        h = ExampleHeader(14, 22, 8)
        assert h.field_a == 14
        assert h.field_b == 22
        assert h.field_c == 8

    def test_initialize_with_keyword_arguments(self):
        h = ExampleHeader(field_a=14, field_b=22, field_c=8)
        assert h.field_a == 14
        assert h.field_b == 22
        assert h.field_c == 8

    def test_initialize_with_positional_and_keyword_arguments(self):
        h = ExampleHeader(14, 22, field_c=8)
        assert h.field_a == 14
        assert h.field_b == 22
        assert h.field_c == 8

    def test_out_of_range_field_values_raises_value_error(self):
        with raises(ValueError):
            ExampleHeader(14, -1, field_c=8)

    def test_illegal_keyword_argument_raises_type_error(self):
        with raises(TypeError):
            ExampleHeader(14, 1, field_x=8)

    def test_ordered_field_names(self):
        assert ExampleHeader.ordered_field_names() == ('field_a', 'field_b', 'field_c')

    @given(a=integers(*LIMITS[SegYType.INT32]),
           b=integers(*LIMITS[SegYType.NNINT32]),
           c=integers(*LIMITS[SegYType.INT32]))
    def test_copy(self, a, b, c):
        h1 = ExampleHeader(a, b, c)
        h2 = copy(h1)
        assert h1 is not h2
        assert h1.field_a == h2.field_a
        assert h1.field_a == h2.field_a
        assert h1.field_a == h2.field_a

    @given(a=integers(*LIMITS[SegYType.INT32]),
           b=integers(*LIMITS[SegYType.NNINT32]),
           c=integers(*LIMITS[SegYType.INT32]))
    def test_repr(self, a, b, c):
        r = repr(ExampleHeader(a, b, c))
        assert str(a) in r
        assert str(b) in r
        assert str(c) in r
        assert 'field_a' in r
        assert 'field_b' in r
        assert 'field_c' in r
        assert 'ExampleHeader' in r
        assert check_balanced(r)

    @given(a=integers(*LIMITS[SegYType.INT32]),
           b=integers(*LIMITS[SegYType.NNINT32]),
           c=integers(*LIMITS[SegYType.INT32]))
    def test_equality(self, a, b, c):
        lhs = ExampleHeader(a, b, c)
        rhs = ExampleHeader(a, b, c)
        assert are_equal(lhs, rhs)

    @given(a=integers(*LIMITS[SegYType.INT32]),
           b=integers(*LIMITS[SegYType.NNINT32]),
           c=integers(*LIMITS[SegYType.INT32]))
    def test_inequality(self, a, b, c):
        assume(a != 0)
        lhs = ExampleHeader(-a, b, c)
        rhs = ExampleHeader(a, b, c)
        assert not are_equal(lhs, rhs)

    def test_inequality_different_type(self):
        h = ExampleHeader(1, 2, 3)
        assert not are_equal(h, 42)

    def test_read_illegal_attribute_raises_attribute_error(self):
        h = ExampleHeader(1, 2, 3)
        with raises(AttributeError):
            _ = h.field_x

    @given(a=integers(*LIMITS[SegYType.INT32]),
           b=integers(*LIMITS[SegYType.NNINT32]),
           c=integers(*LIMITS[SegYType.INT32]))
    def test_pickle_roundtrip(self, a, b, c):
        h1 = ExampleHeader(a, b, c)
        s = pickle.dumps(h1)
        h2 = pickle.loads(s)
        assert are_equal(h1, h2)

    @given(a=integers(*LIMITS[SegYType.INT32]),
           b=integers(*LIMITS[SegYType.NNINT32]),
           c=integers(*LIMITS[SegYType.INT32]))
    def test_pickle_versioning_mismatch_raises_type_error(self, a, b, c):
        h1 = ExampleHeader(a, b, c)
        s = pickle.dumps(h1)
        s = s.replace(b'2.0.0', b'xxxxx')
        with raises(TypeError):
            pickle.loads(s)

    def test_delete_field_raises_attribute_error(self):
        h1 = ExampleHeader(1, 2, 3)
        with raises(AttributeError):
            del h1.field_a


class TestNamedField:

    def test_name(self):
        assert ExampleHeader.field_a.name == 'field_a'

    def test_value_type(self):
        assert ExampleHeader.field_a.value_type == Int32

    def test_offset(self):
        assert ExampleHeader.field_a.offset == 1

    def test_default(self):
        assert ExampleHeader.field_a.default == 0

    def test_doc(self):
        assert inspect.getdoc(ExampleHeader.field_a) == "Field A. This is field A."

    def test_repr(self):
        r = repr(ExampleHeader.field_a)
        assert 'FieldAField' in r
        assert 'name' in r
        assert 'value_type' in r
        assert 'default' in r
        assert 'field_a' in r
        assert 'Int32' in r
        assert '1' in r
        assert '0' in r
        assert check_balanced(r)