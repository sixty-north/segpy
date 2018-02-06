import os
from itertools import zip_longest
from types import SimpleNamespace

import struct
from hypothesis import given, settings, HealthCheck, Phase, assume
import hypothesis.strategies as st
from io import BytesIO
from pytest import raises

from segpy.binary_reel_header import BinaryReelHeader
from segpy.datatypes import DataSampleFormat, SegYType, SEG_Y_TYPE_TO_CTYPE, PY_TYPES, LIMITS
from segpy.encoding import SUPPORTED_ENCODINGS, is_supported_encoding, UnsupportedEncodingError
from segpy.header import are_equal
import segpy.toolkit as toolkit
from segpy.packer import make_header_packer
from segpy.revisions import SegYRevision
from segpy.trace_header import TraceHeaderRev1

from test.dataset_strategy import extended_textual_header
from test.strategies import header, NUMBER_STRATEGY, PRINTABLE_ASCII_ALPHABET


class TestReadExtendedHeadersCounted:

    @given(num_expected=st.integers(max_value=-1),
           encoding=st.sampled_from(SUPPORTED_ENCODINGS))
    def test_negative_num_expected_raises_value_error(self, num_expected, encoding):
        with raises(ValueError):
            toolkit.read_extended_headers_counted(None, num_expected, encoding)

    @given(encoding=st.sampled_from(SUPPORTED_ENCODINGS))
    def test_zero_expected_returns_empty_list(self, encoding):
        headers = toolkit.read_extended_headers_counted(None, num_expected=0, encoding=encoding)
        assert headers == []

    @given(
        data=st.data(),
        count=st.integers(min_value=1, max_value=10),
        encoding=st.sampled_from(SUPPORTED_ENCODINGS))
    @settings(
        suppress_health_check=(HealthCheck.too_slow,),
        deadline=None,
        phases=(Phase.explicit, Phase.reuse, Phase.generate))
    def test_read_header_successfully(self, data, count, encoding):
        written_headers = data.draw(extended_textual_header(count=count))
        with BytesIO() as fh:
            for header in written_headers:
                for line in header:
                    fh.write(line.encode(encoding))
            fh.seek(0)
            read_headers = toolkit.read_extended_headers_counted(fh, count, encoding=encoding)
            assert read_headers == written_headers

    @given(
        data=st.data(),
        count_a=st.integers(min_value=1, max_value=10),
        count_b=st.integers(min_value=1, max_value=10),
        encoding=st.sampled_from(SUPPORTED_ENCODINGS))
    @settings(
        suppress_health_check=(HealthCheck.too_slow,),
        deadline=None,
        phases=(Phase.explicit, Phase.reuse, Phase.generate))
    def test_premature_end_text_stanza_raises_value_error(self, data, count_a, count_b, encoding):
        headers_a = data.draw(extended_textual_header(count=count_a, end_text_stanza_probability=1.0))
        headers_b = data.draw(extended_textual_header(count=count_b))
        with BytesIO() as fh:
            for header in headers_a:
                for line in header:
                    fh.write(line.encode(encoding))
            for header in headers_b:
                for line in header:
                    fh.write(line.encode(encoding))
            fh.seek(0)
            with raises(ValueError):
                toolkit.read_extended_headers_counted(fh, count_a + count_b, encoding=encoding)

    @given(
        data=st.data(),
        count=st.integers(min_value=1, max_value=10),
        encoding=st.sampled_from(SUPPORTED_ENCODINGS),
        random=st.randoms())
    @settings(
        suppress_health_check=(HealthCheck.too_slow,),
        deadline=None,
        phases=(Phase.explicit, Phase.reuse, Phase.generate))
    def test_read_truncated_header_raises_error(self, data, count, encoding, random):
        written_headers = data.draw(extended_textual_header(count=count))
        with BytesIO() as fh:
            for header in written_headers:
                for line in header:
                    fh.write(line.encode(encoding))
            fh.seek(0, os.SEEK_END)
            length = fh.tell()

            truncate_pos = random.randrange(0, length - 1)

            truncated_buffer = fh.getbuffer()[:truncate_pos]
            with BytesIO(truncated_buffer):
                with raises(EOFError):
                    toolkit.read_extended_headers_counted(fh, count, encoding=encoding)
            del truncated_buffer


class TestReadExtendedHeaders:
    @given(
        data=st.data(),
        encoding=st.sampled_from(SUPPORTED_ENCODINGS))
    @settings(
        suppress_health_check=(HealthCheck.too_slow,),
        deadline=None,
        phases=(Phase.explicit, Phase.reuse, Phase.generate))
    def test_uncounted_headers_are_correctly_detected(self, data, encoding):
        binary_header = BinaryReelHeader(num_extended_textual_headers=-1)
        written_headers = data.draw(extended_textual_header())
        with BytesIO() as fh:
            fh.write(b' ' * toolkit.REEL_HEADER_NUM_BYTES)
            for header in written_headers:
                for line in header:
                    fh.write(line.encode(encoding))
            fh.seek(0)
            read_headers = toolkit.read_extended_textual_headers(
                fh, binary_header, encoding=encoding)
            assert read_headers == written_headers

    @given(
        data=st.data(),
        count=st.integers(min_value=1, max_value=10),
        encoding=st.sampled_from(SUPPORTED_ENCODINGS))
    @settings(
        suppress_health_check=(HealthCheck.too_slow,),
        deadline=None,
        phases=(Phase.explicit, Phase.reuse, Phase.generate))
    def test_counted_headers_are_correctly_detected(self, data, count, encoding):
        binary_header = BinaryReelHeader(num_extended_textual_headers=count)
        written_headers = data.draw(extended_textual_header(count=count))
        with BytesIO() as fh:
            fh.write(b' ' * toolkit.REEL_HEADER_NUM_BYTES)
            for header in written_headers:
                for line in header:
                    fh.write(line.encode(encoding))
            fh.seek(0)
            read_headers = toolkit.read_extended_textual_headers(
                fh, binary_header, encoding=encoding)
            assert read_headers == written_headers


class TestBytesPerSample:

    @given(bad_dsf=st.integers(-32768, +32767))
    def test_invalid_bytes_per_sample_field_raises_value_error(self, bad_dsf):
        assume(all(bad_dsf != f for f in DataSampleFormat))  # IntEnum doesn't support the in operator for integers
        fake_header = SimpleNamespace()
        fake_header.data_sample_format = bad_dsf
        with raises(ValueError):
            toolkit.bytes_per_sample(fake_header)

    @given(binary_reel_header=header(BinaryReelHeader))
    def test_valid_bytes_per_sample(self, binary_reel_header):
        bps = toolkit.bytes_per_sample(binary_reel_header)
        assert bps in {1, 2, 4}


@given(binary_reel_header=header(BinaryReelHeader),
       spt=st.integers(min_value=0, max_value=1000))
def test_samples_per_trace(binary_reel_header, spt):
    binary_reel_header.num_samples = spt
    assert toolkit.samples_per_trace(binary_reel_header) == spt


@given(binary_reel_header=header(BinaryReelHeader),
       bps=st.sampled_from((1, 2, 4)))
def test_empty_traces_have_same_length_as_trace_header(binary_reel_header, bps):
    binary_reel_header.num_samples = 0
    assert toolkit.trace_length_bytes(binary_reel_header, bps) == toolkit.TRACE_HEADER_NUM_BYTES


@given(binary_reel_header=header(BinaryReelHeader),
       bps=st.sampled_from((1, 2, 4)))
def test_on_sample_traces_have_same_length_as_trace_header_plus_one_sample(binary_reel_header, bps):
    binary_reel_header.num_samples = 1
    assert toolkit.trace_length_bytes(binary_reel_header, bps) == toolkit.TRACE_HEADER_NUM_BYTES + bps


class TestCatalogTraces:

    def test_non_callable_progress_raises_type_error(self):
        with raises(TypeError):
            toolkit.catalog_traces(None, None, progress=object())


class TestReadTraceHeader:

    @given(trace_header_written=header(TraceHeaderRev1),
           endian=st.sampled_from(('<', '>')))
    def test_read_header_successfully(self, trace_header_written, endian):
        trace_header_packer = make_header_packer(TraceHeaderRev1, endian)
        buffer = trace_header_packer.pack(trace_header_written)
        with BytesIO(buffer) as fh:
            trace_header = toolkit.read_trace_header(fh, trace_header_packer, pos=0)
            assert are_equal(trace_header_written, trace_header)

    @given(trace_header_written=header(TraceHeaderRev1),
           endian=st.sampled_from(('<', '>')),
           random=st.randoms())
    def test_read_truncated_header_raises_eoferror(self, trace_header_written, endian, random):
        trace_header_packer = make_header_packer(TraceHeaderRev1, endian)
        buffer = trace_header_packer.pack(trace_header_written)
        truncate_pos = random.randrange(0, len(buffer) - 1)
        truncated_buffer = buffer[:truncate_pos]
        with BytesIO(truncated_buffer) as fh:
            with raises(EOFError):
                toolkit.read_trace_header(fh, trace_header_packer, pos=0)


class TestReadBinaryValues:

    @given(seg_y_type=st.sampled_from(SegYType),
           num_items=st.integers(min_value=0, max_value=100),
           endian=st.sampled_from(('<', '>')),
           data=st.data())
    def test_read_binary_values_successfully(self, seg_y_type, num_items, endian, data):
        assume(seg_y_type != SegYType.IBM)
        ctype = SEG_Y_TYPE_TO_CTYPE[seg_y_type]
        c_format = ''.join(map(str, (endian, num_items, ctype)))
        py_type = PY_TYPES[seg_y_type]
        min_value, max_value = LIMITS[seg_y_type]
        items_written = data.draw(st.lists(
            elements=NUMBER_STRATEGY[py_type](min_value=min_value, max_value=max_value),
            min_size=num_items, max_size=num_items))
        buffer = struct.pack(c_format, *items_written)
        with BytesIO(buffer) as fh:
            items_read = toolkit.read_binary_values(fh, 0, seg_y_type, num_items, endian)
            assert all(a == b for a, b in zip_longest(items_read, items_read))

    @given(seg_y_type=st.sampled_from(SegYType),
           num_items=st.integers(min_value=1, max_value=100),
           endian=st.sampled_from(('<', '>')),
           data=st.data())
    def test_truncated_read_binary_values_raises_eof_error(self, seg_y_type, num_items, endian, data):
        assume(seg_y_type != SegYType.IBM)
        ctype = SEG_Y_TYPE_TO_CTYPE[seg_y_type]
        c_format = ''.join(map(str, (endian, num_items, ctype)))
        py_type = PY_TYPES[seg_y_type]
        min_value, max_value = LIMITS[seg_y_type]
        items_written = data.draw(st.lists(
            elements=NUMBER_STRATEGY[py_type](min_value=min_value, max_value=max_value),
            min_size=num_items, max_size=num_items))
        buffer = struct.pack(c_format, *items_written)
        truncate_pos = data.draw(st.integers(min_value=0, max_value=max(0, len(buffer) - 1)))
        truncated_buffer = buffer[:truncate_pos]
        with BytesIO(truncated_buffer) as fh:
            with raises(EOFError):
                toolkit.read_binary_values(fh, 0, seg_y_type, num_items, endian)


class TestFormatStandardTextualHeader:

    def test_format_header_successfully(self):
            header = toolkit.format_standard_textual_header(
                                            SegYRevision.REVISION_1,
                                            client="Lundin",
                                            company="Western Geco",
                                            crew_number=123,
                                            processing1="Sixty North AS",
                                            sweep_start_hz=10,
                                            sweep_end_hz=1000,
                                            sweep_length_ms=10000,
                                            sweep_channel_number=3,
                                            sweep_type='spread')
            assert len(header) == 40
            assert all(len(line) == 80 for line in header)

    def test_format_header_with_mismatched_keywords_raises_type_error(self):
        with raises(TypeError):
            toolkit.format_standard_textual_header(
                                            SegYRevision.REVISION_1,
                                            jelly="Strawberry")


class TestParseStandardTextualHeader:

    @given(header_lines=st.lists(elements=st.text(alphabet=PRINTABLE_ASCII_ALPHABET),
                                 min_size=40, max_size=40))
    def test_parse_header_with_wrong_line_length_raises_value_error(self, header_lines):
        assume(all(len(line) != 80 for line in header_lines))
        with raises(ValueError):
            toolkit.parse_standard_textual_header(header_lines)

    @given(header_lines=st.lists(elements=st.text(alphabet=PRINTABLE_ASCII_ALPHABET)))
    def test_parse_header_with_wrong_number_of_lines_raises_value_error(self, header_lines):
        assume(len(header_lines) != 40)
        with raises(ValueError):
            toolkit.parse_standard_textual_header(header_lines)


class TestWriteTextualReelHeader:

    @given(encoding=st.text(alphabet=PRINTABLE_ASCII_ALPHABET))
    def test_unsupported_encoding_raises_unsupported_encoding_error(self, encoding):
        assume(not is_supported_encoding(encoding))
        with raises(UnsupportedEncodingError):
            toolkit.write_textual_reel_header(None, [], encoding)


class TestFormatExtendedTextualHeader:

    @given(encoding=st.text(alphabet=PRINTABLE_ASCII_ALPHABET))
    def test_unsupported_encoding_raises_unsupported_encoding_error(self, encoding):
        assume(not is_supported_encoding(encoding))
        with raises(UnsupportedEncodingError):
            toolkit.format_extended_textual_header('', encoding)


class TestWriteExtendedTextualHeaders:

    @given(encoding=st.text(alphabet=PRINTABLE_ASCII_ALPHABET))
    def test_unsupported_encoding_raises_unsupported_encoding_error(self, encoding):
        assume(not is_supported_encoding(encoding))
        with raises(UnsupportedEncodingError):
            toolkit.write_extended_textual_headers(None, [], encoding)

    @given(pages=st.lists(st.lists(st.text(alphabet=PRINTABLE_ASCII_ALPHABET))),
           encoding=st.sampled_from(SUPPORTED_ENCODINGS))
    def test_line_length_raises_value_error(self, pages, encoding):
        assume(any(len(line) != 80 for page in pages for line in page))
        with BytesIO() as fh:
            with raises(ValueError):
                toolkit.write_extended_textual_headers(fh, pages, encoding)

    @given(pages=st.lists(
        elements=st.lists(
            elements=st.text(alphabet=PRINTABLE_ASCII_ALPHABET, min_size=80, max_size=80),
            max_size=50),
        max_size=5),
        encoding=st.sampled_from(SUPPORTED_ENCODINGS))
    @settings(
        suppress_health_check=(HealthCheck.too_slow,),
        deadline=None,
        phases=(Phase.explicit, Phase.reuse, Phase.generate))
    def test_incorrect_page_length_raises_value_error(self, pages, encoding):
        assume(any(len(page) != 40 for page in pages))
        with BytesIO() as fh:
            with raises(ValueError):
                toolkit.write_extended_textual_headers(fh, pages, encoding)

    @given(pages_written=st.lists(
        elements=st.lists(
            elements=st.text(alphabet=PRINTABLE_ASCII_ALPHABET, min_size=80, max_size=80),
            min_size=40, max_size=40).map(tuple),
        max_size=5),
        encoding=st.sampled_from(SUPPORTED_ENCODINGS))
    @settings(
        suppress_health_check=(HealthCheck.too_slow,),
        deadline=None,
        phases=(Phase.explicit, Phase.reuse, Phase.generate))
    def test_correctly_rounttrip_extended_headers(self, pages_written, encoding):
        with BytesIO() as fh:
            toolkit.write_extended_textual_headers(fh, pages_written, encoding)
            fh.seek(toolkit.REEL_HEADER_NUM_BYTES)
            pages_read = toolkit.read_extended_headers_counted(fh, len(pages_written), encoding)
            assert pages_read == pages_written


class TestPackValues:

    @given(seg_y_type=st.sampled_from(SegYType),
           num_items=st.integers(min_value=1, max_value=100),
           endian=st.sampled_from(('<', '>')),
           data=st.data())
    def test_pack_values(self, seg_y_type, num_items, endian, data):
        assume(seg_y_type not in {SegYType.FLOAT32, SegYType.IBM})
        c_type = SEG_Y_TYPE_TO_CTYPE[seg_y_type]
        c_format = ''.join(map(str, (endian, num_items, c_type)))
        py_type = PY_TYPES[seg_y_type]
        min_value, max_value = LIMITS[seg_y_type]
        items_written = tuple(data.draw(st.lists(
            elements=NUMBER_STRATEGY[py_type](min_value=min_value, max_value=max_value),
            min_size=num_items, max_size=num_items)))
        buffer = toolkit.pack_values(items_written, c_type, endian)
        items_read = struct.unpack(c_format, buffer)
        assert items_written == items_read
