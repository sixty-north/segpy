from unittest.mock import Mock, PropertyMock

import pytest

from segpy.binary_reel_header import BinaryReelHeader
from segpy.dataset import DelegatingDataset
from segpy.datatypes import DataSampleFormat, SegYType
from segpy.header import are_equal
from segpy.trace_header import TraceHeaderRev1


class TestDelegatingDataset:

    @pytest.fixture
    def delegatee(self):
        return Mock()

    def test_source_is_delagatee(self, delegatee):
        dd = DelegatingDataset(delegatee)
        assert dd.source is delegatee

    def test_trace_samples_delegation(self, delegatee):
        delegatee.configure_mock(**{'trace_samples.return_value': [17, 3, 9]})
        trace_index = 42
        start = 5
        stop = 10
        dd = DelegatingDataset(delegatee)
        ts = dd.trace_samples(trace_index, start, stop)
        delegatee.trace_samples.assert_called_once_with(trace_index, start, stop)
        assert ts == [17, 3, 9]

    def test_textual_reel_header_delegation(self, delegatee):
        p = PropertyMock(return_value=['foo'])
        type(delegatee).textual_reel_header = p
        dd = DelegatingDataset(delegatee)
        trh = dd.textual_reel_header
        p.assert_called_once_with()
        assert trh == ['foo']

    def test_binary_reel_header_delegation(self, delegatee):
        p = PropertyMock(return_value=BinaryReelHeader())
        type(delegatee).binary_reel_header = p
        dd = DelegatingDataset(delegatee)
        brh = dd.binary_reel_header
        p.assert_called_once_with()
        assert are_equal(brh, BinaryReelHeader())

    def test_trace_header_delegation(self, delegatee):
        delegatee.configure_mock(**{'trace_header.return_value': TraceHeaderRev1()})
        trace_index = 42
        dd = DelegatingDataset(delegatee)
        ts = dd.trace_header(trace_index)
        delegatee.trace_header.assert_called_once_with(trace_index)
        assert are_equal(ts, TraceHeaderRev1())

    def test_trace_indexes_delegation(self, delegatee):
        delegatee.configure_mock(**{'trace_indexes.return_value': range(1, 900)})
        dd = DelegatingDataset(delegatee)
        ti = dd.trace_indexes()
        delegatee.trace_indexes.assert_called_once_with()
        assert ti == range(1, 900)

    def test_num_traces_delegation(self, delegatee):
        delegatee.configure_mock(**{'num_traces.return_value': 543})
        dd = DelegatingDataset(delegatee)
        nt = dd.num_traces()
        delegatee.num_traces.assert_called_once_with()
        assert nt == 543

    def test_dimensionality_header_delegation(self, delegatee):
        p = PropertyMock(return_value=3)
        type(delegatee).dimensionality = p
        dd = DelegatingDataset(delegatee)
        d = dd.dimensionality
        p.assert_called_once_with()
        assert d == 3

    def test_extended_textual_header_delegation(self, delegatee):
        p = PropertyMock(return_value=['Hello', 'World!'])
        type(delegatee).extended_textual_header = p
        dd = DelegatingDataset(delegatee)
        eth = dd.extended_textual_header
        p.assert_called_once_with()
        assert eth == ['Hello', 'World!']

    def test_encoding_delegation(self, delegatee):
        p = PropertyMock(return_value='ascii')
        type(delegatee).encoding = p
        dd = DelegatingDataset(delegatee)
        e = dd.encoding
        p.assert_called_once_with()
        assert e == 'ascii'

    def test_endian_delegation(self, delegatee):
        p = PropertyMock(return_value='<')
        type(delegatee).endian = p
        dd = DelegatingDataset(delegatee)
        e = dd.endian
        p.assert_called_once_with()
        assert e == '<'

    def test_data_sample_format_ibm(self, delegatee):
        p = PropertyMock(return_value=BinaryReelHeader(data_sample_format=DataSampleFormat.IBM))
        type(delegatee).binary_reel_header = p
        dd = DelegatingDataset(delegatee)
        dsf_read = dd.data_sample_format
        assert dsf_read == SegYType.IBM

    def test_data_sample_format_ieee(self, delegatee):
        p = PropertyMock(return_value=BinaryReelHeader(data_sample_format=DataSampleFormat.FLOAT32))
        type(delegatee).binary_reel_header = p
        dd = DelegatingDataset(delegatee)
        dsf_read = dd.data_sample_format
        assert dsf_read == SegYType.FLOAT32

    def test_data_sample_format_int8(self, delegatee):
        p = PropertyMock(return_value=BinaryReelHeader(data_sample_format=DataSampleFormat.INT8))
        type(delegatee).binary_reel_header = p
        dd = DelegatingDataset(delegatee)
        dsf_read = dd.data_sample_format
        assert dsf_read == SegYType.INT8

    def test_data_sample_format_int16(self, delegatee):
        p = PropertyMock(return_value=BinaryReelHeader(data_sample_format=DataSampleFormat.INT16))
        type(delegatee).binary_reel_header = p
        dd = DelegatingDataset(delegatee)
        dsf_read = dd.data_sample_format
        assert dsf_read == SegYType.INT16

    def test_data_sample_format_int32(self, delegatee):
        p = PropertyMock(return_value=BinaryReelHeader(data_sample_format=DataSampleFormat.INT32))
        type(delegatee).binary_reel_header = p
        dd = DelegatingDataset(delegatee)
        dsf_read = dd.data_sample_format
        assert dsf_read == SegYType.INT32

    def test_data_sample_format_description_ieee(self, delegatee):
        p = PropertyMock(return_value=BinaryReelHeader(data_sample_format=DataSampleFormat.FLOAT32))
        type(delegatee).binary_reel_header = p
        dd = DelegatingDataset(delegatee)
        dsfd = dd.data_sample_format_description
        assert dsfd == "IEEE float32"
