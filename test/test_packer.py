import pickle
from hypothesis import given
from hypothesis.strategies import sampled_from
from pytest import raises

import segpy
from segpy.field_types import Int32, NNInt32
from segpy.header import Header, field, are_equal
from segpy.packer import compile_struct, make_header_packer, BijectiveHeaderPacker, SurjectiveHeaderPacker
from test.predicates import check_balanced


class PickleableHeader(Header):
    START_OFFSET_IN_BYTES = 1

    field_a = field(Int32, 1, 0, "Field A.")
    field_b = field(NNInt32, 5, 0, "Field B.")
    field_c = field(Int32, 1, 0, "Field C.")


class TestCompileStruct:

    def test_compile_with_negative_start_offset_raises_value_error(self):
        with raises(ValueError):
            compile_struct(None, -1, 1)

    def test_compile_with_non_positive_length_raises_value_error(self):
        with raises(ValueError):
            compile_struct(None, 0, 0)

    def test_compile_empty_header_raises_type_error(self):

        class EmptyHeader(Header):
            pass

        with raises(TypeError):
            compile_struct(EmptyHeader)

    def test_compile_header_with_too_short_length_raises_value_error(self):

        class ShortHeader(Header):

            START_OFFSET_IN_BYTES = 1
            LENGTH_IN_BYTES = 3

            field_a = field(Int32, 1, 0, "Field A.")

        with raises(ValueError):
            compile_struct(ShortHeader, ShortHeader.START_OFFSET_IN_BYTES, ShortHeader.LENGTH_IN_BYTES)

    def test_compile_header_with_partially_overlapping_fields_raises_value_error(self):

        class OverlappingFieldsHeader(Header):

            field_a = field(Int32, 1, 0, "Field A.")
            field_b = field(Int32, 3, 0, "Field B.")

        with raises(ValueError):
            compile_struct(OverlappingFieldsHeader)

    def test_compile_header_coincident_fields_with_different_types_raises_type_error(self):

        class CoincidentFieldsWithDifferentTypesHeader(Header):
            field_a = field(Int32, 1, 0, "Field A.")
            field_b = field(NNInt32, 1, 0, "Field B.")

        with raises(TypeError):
            compile_struct(CoincidentFieldsWithDifferentTypesHeader)

    @given(endian=sampled_from(('<', '>')))
    def test_compile_bijective_header_packer_successfully(self, endian):

        class BijectiveHeader(Header):
            field_a = field(Int32, 1, 0, "Field A.")
            field_b = field(NNInt32, 5, 0, "Field B.")

        cformat, field_name_allocations = compile_struct(BijectiveHeader, 1, endian=endian)
        assert cformat[0] == endian
        assert cformat[1] == 'i'
        assert cformat[2] == 'I'
        assert field_name_allocations == [['field_a'], ['field_b']]

    @given(endian=sampled_from(('<', '>')))
    def test_compile_surjective_header_packer_successfully(self, endian):

        class SurjectiveHeader(Header):
            field_a = field(Int32, 1, 0, "Field A.")
            field_b = field(NNInt32, 5, 0, "Field B.")
            field_c = field(Int32, 1, 0, "Field C.")

        cformat, field_name_allocations = compile_struct(SurjectiveHeader, 1, endian=endian)
        assert cformat[0] == endian
        assert cformat[1] == 'i'
        assert field_name_allocations == [['field_a','field_c'], ['field_b']]


class TestMakeHeaderPacker:

    def test_make_bijective_header_packer_successfully(self):

        class BijectiveHeader(Header):
            field_a = field(Int32, 1, 0, "Field A.")
            field_b = field(NNInt32, 5, 0, "Field B.")

        packer = make_header_packer(BijectiveHeader)
        assert isinstance(packer, BijectiveHeaderPacker)
        assert packer.header_format_class == BijectiveHeader

    def test_make_surjective_header_packer_successfully(self):

        class SurjectiveHeader(Header):
            field_a = field(Int32, 1, 0, "Field A.")
            field_b = field(NNInt32, 5, 0, "Field B.")
            field_c = field(Int32, 1, 0, "Field C.")

        packer = make_header_packer(SurjectiveHeader)
        assert isinstance(packer, SurjectiveHeaderPacker)
        assert packer.header_format_class == SurjectiveHeader


class TestHeaderPacker:

    def test_pack_incorrect_type(self):
        class BijectiveHeader(Header):
            START_OFFSET_IN_BYTES = 1

            field_a = field(Int32, 1, 0, "Field A.")
            field_b = field(NNInt32, 5, 0, "Field B.")

        packer = make_header_packer(BijectiveHeader, endian='>')
        with raises(TypeError):
            packer.pack(None)

    def test_pack_bijective(self):

        class BijectiveHeader(Header):
            START_OFFSET_IN_BYTES = 1

            field_a = field(Int32, 1, 0, "Field A.")
            field_b = field(NNInt32, 5, 0, "Field B.")

        packer = make_header_packer(BijectiveHeader, endian='>')
        bh = BijectiveHeader(field_a=0x12345678, field_b=0x01357932)
        buffer = packer.pack(bh)
        assert buffer == bytes((0x12, 0x34, 0x56, 0x78, 0x01, 0x35, 0x79, 0x32))

    def test_pack_surjective(self):

        class SurjectiveHeader(Header):
            START_OFFSET_IN_BYTES = 1

            field_a = field(Int32, 1, 0, "Field A.")
            field_b = field(NNInt32, 5, 0, "Field B.")
            field_c = field(Int32, 1, 0, "Field C.")

        packer = make_header_packer(SurjectiveHeader, endian='>')
        bh = SurjectiveHeader(field_a=0x12345678, field_b=0x01357932, field_c=0x12345678)
        buffer = packer.pack(bh)
        assert buffer == bytes((0x12, 0x34, 0x56, 0x78, 0x01, 0x35, 0x79, 0x32))

    def test_pack_inconsistent_surjective_raises_value_error(self):

        class SurjectiveHeader(Header):
            START_OFFSET_IN_BYTES = 1

            field_a = field(Int32, 1, 0, "Field A.")
            field_b = field(NNInt32, 5, 0, "Field B.")
            field_c = field(Int32, 1, 0, "Field C.")

        packer = make_header_packer(SurjectiveHeader, endian='>')
        bh = SurjectiveHeader(field_a=0x12345678, field_b=0x01357932, field_c=0x52345678)
        with raises(ValueError):
            packer.pack(bh)

    def test_unpack_bijective_header(self):

        class BijectiveHeader(Header):
            START_OFFSET_IN_BYTES = 1

            field_a = field(Int32, 1, 0, "Field A.")
            field_b = field(NNInt32, 5, 0, "Field B.")

        packer = make_header_packer(BijectiveHeader, endian='>')
        buffer = bytes((0x12, 0x34, 0x56, 0x78, 0x01, 0x35, 0x79, 0x32))
        header = packer.unpack(buffer)
        assert are_equal(header, BijectiveHeader(field_a=0x12345678, field_b=0x01357932))

    def test_unpack_surjective_header(self):

        class SurjectiveHeader(Header):
            START_OFFSET_IN_BYTES = 1

            field_a = field(Int32, 1, 0, "Field A.")
            field_b = field(NNInt32, 5, 0, "Field B.")
            field_c = field(Int32, 1, 0, "Field C.")

        packer = make_header_packer(SurjectiveHeader, endian='>')
        buffer = bytes((0x12, 0x34, 0x56, 0x78, 0x01, 0x35, 0x79, 0x32))
        header = packer.unpack(buffer)
        assert are_equal(header, SurjectiveHeader(field_a=0x12345678, field_b=0x01357932, field_c=0x12345678))

    def test_repr(self):

        class MyHeader(Header):
            START_OFFSET_IN_BYTES = 1

            field_a = field(Int32, 1, 0, "Field A.")
            field_b = field(NNInt32, 5, 0, "Field B.")
            field_c = field(Int32, 1, 0, "Field C.")

        packer = make_header_packer(MyHeader, endian='>')
        r = repr(packer)
        assert 'SurjectiveHeaderPacker' in r
        assert 'MyHeader' in r
        assert check_balanced(r)


    def test_pickle_roundtrip(self):
        packer1 = make_header_packer(PickleableHeader, endian='>')
        s = pickle.dumps(packer1)
        packer2 = pickle.loads(s)
        assert packer1._header_format_class == packer2._header_format_class
        assert packer1._structure.format == packer2._structure.format
        assert packer1._field_name_allocations == packer2._field_name_allocations

    def test_pickle_versioning_mismatch_raises_type_error(self):
        packer1 = make_header_packer(PickleableHeader, endian='>')
        s = pickle.dumps(packer1)
        s = s.replace(segpy.__version__.encode('ascii'), b'xxxxx')
        with raises(TypeError):
            pickle.loads(s)
