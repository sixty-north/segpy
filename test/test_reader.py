"""Tests for segpy.reader.
"""

import io
import pathlib
import pickle
from unittest.mock import MagicMock, patch

from hypothesis import assume, given, HealthCheck, Phase, settings
import hypothesis.strategies as ST
import pytest
from segpy.header import are_equal
from segpy.reader import (create_reader, SegYReader, SegYReader2D,
                          SegYReader3D, _load_reader_from_cache,
                          _save_reader_to_cache)
from segpy.toolkit import bytes_per_sample, REEL_HEADER_NUM_BYTES
from segpy.trace_header import TraceHeaderRev0, TraceHeaderRev1
from segpy.writer import write_segy
from .dataset_strategy import dataset, dataset_2d, diagonal_dataset_3d


@pytest.fixture
def min_reader_data():
    "Binary data of minimal size to satisfy `create_reader`."
    return io.BytesIO(b'0' * REEL_HEADER_NUM_BYTES)


@pytest.fixture
def tempdir(tmpdir):
    return pathlib.Path(str(tmpdir))


@pytest.fixture(params=['<', '>'])
def endian(request):
    return request.param


@pytest.fixture(params=[1, 2, 3])
def dset(request):
    return dataset(num_dims=request.param).example()


# To test:
# - cache directory
# - progress callback
# - round-tripping of data
# - reader attributes
# - 1, 2, and 3D data
# - Dimensionality heuristics (i.e. passing `None` as dimensionality.)


class Test_create_reader_Exceptions:
    """Tests for exceptions that `create_reader` can throw.
    """
    def test_type_error_on_non_binary_handle(self):
        handle = io.TextIOWrapper(io.BytesIO(), encoding='utf-8')
        with pytest.raises(TypeError):
            create_reader(handle)

    def test_type_error_on_non_seekable_handle(self):
        with pytest.raises(TypeError):
            create_reader(io.RawIOBase())

    def test_value_error_on_closed_handle(self):
        handle = io.BytesIO()
        handle.close()
        with pytest.raises(ValueError):
            create_reader(handle)

    def test_value_error_on_short_file(self):
        handle = io.BytesIO(b'')
        with pytest.raises(ValueError):
            create_reader(handle)

    @given(endian=ST.text())
    def test_value_error_on_invalid_endian(self, endian, min_reader_data):
        assume(endian not in ('<', '>'))
        with pytest.raises(ValueError):
            create_reader(min_reader_data,
                          endian=endian)

    def test_type_error_if_progress_callback_not_callable(self, min_reader_data):
        with pytest.raises(TypeError):
            create_reader(min_reader_data,
                          progress='not callable')

    @given(dims=ST.integers())
    def test_value_error_on_invalid_dimensionality(self, dims, min_reader_data):
        assume(dims not in (None, 1, 2, 3))
        with pytest.raises(ValueError):
            create_reader(min_reader_data,
                          dimensionality=dims)


class TestReaderCache:
    def test_cache_is_created_when_requested(self, dset, tempdir):
        segy_file = str(tempdir / 'test.segy')
        cache_dir = '.segy_cache'
        cache_path = tempdir / cache_dir

        with open(segy_file, mode='wb') as fh:
            write_segy(fh, dset)

        assert not cache_path.exists()

        with open(segy_file, mode='rb') as fh:
            reader = create_reader(fh, cache_directory=cache_dir)

        assert cache_path.exists()

    def test_cache_used_if_found(self, tempdir):
        dset1 = dataset(num_dims=2).example()
        dset2 = dataset(num_dims=2).example()

        # This is hacky. We want to verify that create_reader will use a
        # chached reader if one exists, but we don't really have a way to
        # determine that directly (without timing, perhaps). So we're going to
        # try to trick the system. First we'll save one dataset and read it to
        # generate a cache. Then we'll do the same with another dataset . Then
        # we'll copy the first cache over the second, making sure to use the
        # right filename (since it's derived from the sha1 of the dataset).
        # Finally, we'll load the second dataset and request that the cache is
        # used. The returned reader should look like the first dataset, i.e.
        # the one who's cache we copied.

        # create a reliably different dset. hypothesis likes to make them
        # entirely equal.
        dset2.binary_reel_header.reel_num = 1 if dset1.binary_reel_header.reel_num == 0 else 0

        # generate the cache for the first dataset
        segy_dir1 = tempdir / '1'
        segy_dir1.mkdir()
        segy_file1 = str(segy_dir1 / 'test.segy')
        cache_dir = '.segy_cache'
        with open(segy_file1, mode='wb') as fh:
            write_segy(fh, dset1)
        with open(segy_file1, mode='rb') as fh:
            create_reader(fh, cache_directory=cache_dir)

        # generate the cache for the second dataset
        segy_dir2 = tempdir / '2'
        segy_dir2.mkdir()
        segy_file2 = str(segy_dir2 / 'test.segy')
        with open(segy_file2, mode='wb') as fh:
            write_segy(fh, dset2)
        with open(segy_file2, mode='rb') as fh:
            create_reader(fh, cache_directory=cache_dir)

        # Replace the second cache with the first, preserving the filename.
        cache_path1 = segy_dir1 / cache_dir
        cache_file1 = next(cache_path1.iterdir())
        cache_path2 = segy_dir2 / cache_dir
        cache_file2 = next(cache_path2.iterdir())
        cache_file1.replace(cache_file2)

        # Now when we load the second dataset, we should get the cache of the
        # first. Sneaky!
        with open(segy_file2, mode='rb') as fh:
            reader = create_reader(
                fh,
                dimensionality=dset2.dimensionality,
                cache_directory=cache_dir)
            _compare_datasets(dset1, reader,
                              compare_dimensionality=False)

    def test_type_error_on_non_reader_cache_file(self, dset, tempdir):
        segy_file = str(tempdir / 'test.segy')
        cache_dir = '.segy_cache'
        with open(segy_file, mode='wb') as fh:
            write_segy(fh, dset)

        with open(segy_file, mode='rb') as fh:
            create_reader(fh, cache_directory=cache_dir)

        cache_dir = tempdir / cache_dir
        cache_file = next(cache_dir.iterdir())
        with open(str(cache_file), mode='wb') as fh:
            pickle.dump('not a reader', fh)

        with pytest.raises(TypeError):
            with open(segy_file, mode='rb') as fh:
                create_reader(fh, cache_directory=cache_dir)

    def test_reading_when_cache_dir_is_empty(self, dset, tempdir):
        segy_file = str(tempdir / 'test.segy')
        cache_dir = '.segy_cache'
        with open(segy_file, mode='wb') as fh:
            write_segy(fh, dset)

        with open(segy_file, mode='rb') as fh:
            create_reader(fh, cache_directory=cache_dir)

        cache_dir = tempdir / cache_dir
        for cache_file in cache_dir.iterdir():
            cache_file.unlink()

        with open(segy_file, mode='rb') as fh:
            reader = create_reader(fh,
                                   dimensionality=dset.dimensionality,
                                   cache_directory=cache_dir)
            _compare_datasets(reader, dset)

    def test_save_unpickleable_object_to_cache(self, tempdir):
        # TODO: I'm a bit dubious about this test and/or the code it tests. We have
        # code that tries to pickle a reader into a cache file, and we have a test
        # to see if the pickling fails. But I don't see how pickling could fail
        # unless we have a SegYReader class that doesn't pickle. This seems more
        # like an assertion/programmer error than a exception we want to catch.
        #
        # To wit: we have to call implementation functions directly here because I
        # can find no way to trigger the exception through the public API.

        unpickleable = lambda y: 42
        cache_file_path = tempdir / 'segy_cache'
        _save_reader_to_cache(unpickleable, cache_file_path)
        assert cache_file_path.stat().st_size == 0

    @patch('pathlib.Path.open',
           MagicMock(side_effect=OSError('mock OSError')))
    def test_OSError_during_cache_creation(self, tempdir):
        cache_file_path = tempdir / 'segy_cache'
        _save_reader_to_cache('dummy value', cache_file_path)
        assert pathlib.Path.open.called
        assert not cache_file_path.exists()

    @patch('pickle.load',
           MagicMock(side_effect=Exception('artificial exception')))
    def test_cache_file_cleared_when_not_a_valid_pickle(self, tempdir):
        filename = tempdir / 'cache_file'
        with open(str(filename), mode='wb') as fh:
            fh.write(b'not a pickle')
        _load_reader_from_cache(filename, tempdir / 'segy_file')
        assert pickle.load.called
        assert not filename.exists()

    @patch('pathlib.Path.unlink',
           MagicMock(side_effect=OSError('artificial OSError')))
    @patch('pickle.load',
           MagicMock(side_effect=Exception('artificial exception')))
    def test_cache_file_not_cleared_on_OSError(self, tempdir):
        filename = tempdir / 'cache_file'
        with open(str(filename), mode='wb') as fh:
            fh.write(b'not a pickle')
        _load_reader_from_cache(filename, tempdir / 'segy_file')
        assert pathlib.Path.unlink.called
        assert pickle.load.called
        assert filename.exists()


def test_reading_from_non_file(dset):
    handle = io.BytesIO()
    write_segy(handle, dset)

    handle.seek(0)
    reader = create_reader(handle, dimensionality=dset.dimensionality)

    _compare_datasets(reader, dset)


def _dataset_round_trip(rootdir, dataset, compare_dimensionality=True):
    """Write `dataset` to a file in `rootdir`, read it back in, and compare the
    original with the loaded version.
    """
    segy_file = str(rootdir / 'test.segy')

    with open(segy_file, mode='bw') as fh:
        write_segy(fh, dataset)

    with open(segy_file, mode='br') as fh:
        reader = create_reader(
            fh,
            trace_header_format=dataset._trace_header_format,
            dimensionality=dataset.dimensionality)

        _compare_datasets(dataset, reader, compare_dimensionality)


def _compare_datasets(ds1, ds2, compare_dimensionality=True):
    assert ds1.textual_reel_header == ds2.textual_reel_header
    assert are_equal(ds1.binary_reel_header, ds2.binary_reel_header)
    assert ds1.extended_textual_header == ds2.extended_textual_header
    assert ds1.data_sample_format == ds2.data_sample_format
    assert ds1.data_sample_format_description == ds2.data_sample_format_description

    assert sorted(ds1.trace_indexes()) == sorted(ds2.trace_indexes())
    assert ds1.num_traces() == ds2.num_traces()
    assert len(list(ds1.trace_indexes())) == ds1.num_traces()
    assert len(list(ds2.trace_indexes())) == ds2.num_traces()
    assert sorted(ds1.trace_indexes()) == sorted(ds2.trace_indexes())

    for trace_index in ds1.trace_indexes():
        assert are_equal(ds1.trace_header(trace_index),
                         ds2.trace_header(trace_index))
        assert list(ds1.trace_samples(trace_index)) == list(ds2.trace_samples(trace_index))

    if compare_dimensionality:
        assert ds1.dimensionality == ds2.dimensionality


@given(dataset(num_dims=1))
@settings(
    max_examples=10,
    suppress_health_check=(HealthCheck.too_slow,),
    deadline=None,
    phases=(Phase.explicit, Phase.reuse, Phase.generate),
)
def test_round_trip_1D(tempdir, dataset):
    _dataset_round_trip(tempdir, dataset)


@given(dataset(num_dims=2))
@settings(
    max_examples=10,
    suppress_health_check=(HealthCheck.too_slow,),
    deadline=None,
    phases=(Phase.explicit, Phase.reuse, Phase.generate),
)
def test_round_trip_2D(tempdir, dataset):
    _dataset_round_trip(tempdir, dataset)


@given(dataset(num_dims=3))
@settings(
    max_examples=10,
    suppress_health_check=(HealthCheck.too_slow,),
    deadline=None,
    phases=(Phase.explicit, Phase.reuse, Phase.generate),
)
def test_round_trip_3D(tempdir, dataset):
    _dataset_round_trip(tempdir, dataset)


def test_SegYReader_throws_TypeError_when_trace_offset_catalog_is_None():
    with pytest.raises(TypeError):
        SegYReader(
            fh=object(),
            textual_reel_header=object(),
            binary_reel_header=object(),
            extended_textual_headers=object(),
            trace_offset_catalog=None,
            trace_length_catalog=object(),
            trace_header_format=TraceHeaderRev0,
            encoding=object())


def test_SegYReader_throws_TypeError_when_trace_length_catalog_is_None():
    with pytest.raises(TypeError):
        SegYReader(
            fh=object(),
            textual_reel_header=object(),
            binary_reel_header=object(),
            extended_textual_headers=object(),
            trace_offset_catalog=object(),
            trace_length_catalog=None,
            trace_header_format=TraceHeaderRev0,
            encoding=object())


def test_SegYReader_throws_TypeError_when_pickling_from_closed_file_handle(dset):
    fh = io.BytesIO()
    write_segy(fh, dset)
    fh.seek(0)
    reader = create_reader(fh)
    fh.close()

    with pytest.raises(TypeError):
        pickle.dumps(reader)


def test_SegYReader_throws_TypeError_if_pickled_without_real_file_handle(dset):
    fh = io.BytesIO()
    write_segy(fh, dset)

    fh.seek(0)
    reader = create_reader(fh, cache_directory=None)

    with pytest.raises(TypeError):
        pickle.dumps(reader)


def test_cache_version_mismatch_throws_TypeError(dset, tempdir):
    segy_file = tempdir / 'segy'
    cache_dir = 'cache_dir'
    with open(str(segy_file), mode='wb') as fh:
        write_segy(fh, dset)

    # Create reader to force creation of cache
    with open(str(segy_file), mode='rb') as fh:
        reader = create_reader(fh, cache_directory=cache_dir)
        state_dict = reader.__getstate__()
        state_dict['__version__'] = state_dict['__version__'] * 2
        with pytest.raises(TypeError):
            reader.__setstate__(state_dict)


def test_TypeError_unpickling_cache_with_missing_segy_file(dset, tempdir):
    segy_file = tempdir / 'segy'
    cache_dir = 'cache_dir'

    with open(str(segy_file), mode='wb') as fh:
        write_segy(fh, dset)

    # Force creation of cache
    with open(str(segy_file), mode='rb') as fh:
        create_reader(fh, cache_directory=cache_dir)

    # Delete the segy file
    segy_file.unlink()

    # Try to unpickle the cache
    cache_path = tempdir / cache_dir
    cache_file = next(cache_path.iterdir())
    with open(str(cache_file), mode='rb') as fh:
        with pytest.raises(TypeError):
            pickle.load(fh)


def test_num_cdps_is_correct():
    dset = dataset_2d().example()
    fh = io.BytesIO()
    write_segy(fh, dset)
    reader = create_reader(fh, dimensionality=2)
    assert reader.num_traces() == reader.num_cdps()


def test_all_cdps_have_a_trace_index(dset):
    fh = io.BytesIO()
    write_segy(fh, dset)
    reader = create_reader(fh, dimensionality=2)
    for cdp_number in reader.cdp_numbers():
        assert reader.has_trace_index(cdp_number)


def test_all_cdps_map_to_a_trace_index(dset):
    fh = io.BytesIO()
    write_segy(fh, dset)
    fh.seek(0)
    reader = create_reader(fh, dimensionality=2)
    for cdp_number in reader.cdp_numbers():
        reader.trace_index(cdp_number)


def test_SegYReader2D_raises_TypeError_on_null_cdp_catalog():
    dataset = dataset_2d().example()
    fh = io.BytesIO()
    write_segy(fh, dataset)
    fh.seek(0)
    reader = create_reader(fh, dimensionality=2)

    fh.seek(0)
    with pytest.raises(TypeError):
        SegYReader2D(
            fh=fh,
            textual_reel_header=reader.textual_reel_header,
            binary_reel_header=reader.binary_reel_header,
            extended_textual_headers=reader._extended_textual_headers,
            trace_offset_catalog=reader._trace_offset_catalog,
            trace_length_catalog=reader._trace_length_catalog,
            cdp_catalog=None,
            trace_header_format=reader.trace_header_format_class,
            encoding=reader.encoding)


def test_SegYReader3D_raises_TypeError_on_null_line_catalog():
    dataset = diagonal_dataset_3d().example()
    fh = io.BytesIO()
    write_segy(fh, dataset)
    fh.seek(0)
    reader = create_reader(fh, dimensionality=2)

    fh.seek(0)
    with pytest.raises(TypeError):
        SegYReader3D(
            fh=fh,
            textual_reel_header=reader.textual_reel_header,
            binary_reel_header=reader.binary_reel_header,
            extended_textual_headers=reader._extended_textual_headers,
            trace_offset_catalog=reader._trace_offset_catalog,
            trace_length_catalog=reader._trace_length_catalog,
            line_catalog=None,
            trace_header_format=reader.trace_header_format_class,
            encoding=reader.encoding)


class Test_trace_samples_Exceptions:
    "Tests for various exceptions from trace_samples()."

    def test_ValueError_on_out_of_range_trace_index(self, dset):
        fh = io.BytesIO()

        write_segy(fh, dset)

        fh.seek(0)
        reader = create_reader(fh)

        with pytest.raises(ValueError):
            reader.trace_samples(-1)

        with pytest.raises(ValueError):
            reader.trace_samples(reader.num_traces())

    def test_ValueError_on_out_of_range_stop_sample(self, dset):
        assume(dset.num_traces() > 0)

        fh = io.BytesIO()
        write_segy(fh, dset)

        fh.seek(0)
        reader = create_reader(fh)

        with pytest.raises(ValueError):
            reader.trace_samples(0, stop=-1)

        with pytest.raises(ValueError):
            reader.trace_samples(0, stop=reader.num_trace_samples(0) + 1)

    def test_ValueError_on_out_of_range_start_sample(self, dset):
        assume(dset.num_traces() > 0)

        fh = io.BytesIO()

        write_segy(fh, dset)

        fh.seek(0)
        reader = create_reader(fh)
        with pytest.raises(ValueError):
            reader.trace_samples(0, start=-1)

        with pytest.raises(ValueError):
            reader.trace_samples(0, start=reader.num_trace_samples(0) + 1)


def test_trace_header_raises_ValueError_on_out_of_range(dset):
    fh = io.BytesIO()
    write_segy(fh, dset)

    fh.seek(0)
    reader = create_reader(fh)

    with pytest.raises(ValueError):
        reader.trace_header(-1)

    with pytest.raises(ValueError):
        reader.trace_header(reader.num_traces() + 1)


def test_trace_header_format_is_requested_format(dset):
    fh = io.BytesIO()
    write_segy(fh, dset)

    fh.seek(0)
    reader = create_reader(
        fh,
        trace_header_format=TraceHeaderRev1)

    # TODO: Currently we only generate datasets with rev1 headers. We need to
    # fix this.
    assert reader.trace_header_format_class is TraceHeaderRev1


def test_filename_correctly_reported_for_normal_files(tempdir, dset):
    segy_file = str(tempdir / 'segy')
    with open(segy_file, mode='wb') as fh:
        write_segy(fh, dset)

    with open(segy_file, mode='rb') as fh:
        reader = create_reader(fh)
        assert reader.filename == segy_file


def test_filename_reports_unknown_when_filename_unavailable(dset):
    fh = io.BytesIO()
    write_segy(fh, dset)

    fh.seek(0)
    reader = create_reader(fh)
    assert reader.filename == '<unknown>'


def test_segy_revision_is_correct(dset):
    fh = io.BytesIO()
    write_segy(fh, dset)

    fh.seek(0)
    reader = create_reader(fh)
    assert reader.revision == dset.binary_reel_header.format_revision_num


def test_SegYReader_bytes_per_sample_is_correct(dset):
    fh = io.BytesIO()
    write_segy(fh, dset)

    fh.seek(0)
    reader = create_reader(fh)
    assert reader.bytes_per_sample == bytes_per_sample(dset.binary_reel_header)


def test_SegYReader_endianness_is_correct(dset, endian):
    fh = io.BytesIO()
    write_segy(fh, dset, endian=endian)
    fh.seek(0)
    reader = create_reader(fh, endian=endian)
    assert reader.endian == endian


@patch('segpy.reader.guess_textual_header_encoding',
       MagicMock(return_value=None))
def test_create_reader_will_default_to_ascii_encoding(dset):
    fh = io.BytesIO()
    write_segy(fh, dset)
    reader = create_reader(fh, encoding=None)
    assert reader.encoding == 'ascii'


@given(dataset_2d(valid_cdp_catalog=True))
@settings(
    max_examples=10,
    suppress_health_check=(HealthCheck.too_slow,),
    deadline=None,
    phases=(Phase.explicit, Phase.reuse, Phase.generate),
)
def test_heuristic_for_2D_works_as_expected(dset):
    fh = io.BytesIO()
    write_segy(fh, dset)
    fh.seek(0)
    reader = create_reader(fh, dimensionality=None)
    assert reader.dimensionality == 2


@given(diagonal_dataset_3d(valid_line_catalog=True))
@settings(
    max_examples=10,
    suppress_health_check=(HealthCheck.too_slow,),
    deadline=None,
    phases=(Phase.explicit, Phase.reuse, Phase.generate),
)
def test_heuristic_for_3D_works_as_expected(dset):
    fh = io.BytesIO()
    write_segy(fh, dset)
    fh.seek(0)
    reader = create_reader(fh, dimensionality=None)
    assert reader.dimensionality == 3


@given(diagonal_dataset_3d(valid_line_catalog=True))
@settings(
    max_examples=10,
    suppress_health_check=(HealthCheck.too_slow,),
    deadline=None,
    phases=(Phase.explicit, Phase.reuse, Phase.generate),
)
def test_num_inlines_is_correct(dset):
    fh = io.BytesIO()
    write_segy(fh, dset)
    fh.seek(0)
    reader = create_reader(fh)
    assert reader.num_inlines() == dset.num_traces()


@given(diagonal_dataset_3d(valid_line_catalog=True))
@settings(
    max_examples=10,
    suppress_health_check=(HealthCheck.too_slow,),
    deadline=None,
    phases=(Phase.explicit, Phase.reuse, Phase.generate),
)
def test_num_xlines_is_correct(dset):
    fh = io.BytesIO()
    write_segy(fh, dset)
    fh.seek(0)
    reader = create_reader(fh)
    assert reader.num_xlines() == dset.num_traces()


@given(diagonal_dataset_3d(valid_line_catalog=True))
@settings(
    max_examples=10,
    suppress_health_check=(HealthCheck.too_slow,),
    deadline=None,
    phases=(Phase.explicit, Phase.reuse, Phase.generate),
)
def test_inline_xline_numbers_is_correct(dset):
    fh = io.BytesIO()
    write_segy(fh, dset)
    fh.seek(0)
    reader = create_reader(fh)
    assert sorted(reader.inline_xline_numbers()) == sorted((idx, idx) for idx in range(dset.num_traces()))


@given(diagonal_dataset_3d(valid_line_catalog=True))
@settings(
    max_examples=10,
    suppress_health_check=(HealthCheck.too_slow,),
    deadline=None,
    phases=(Phase.explicit, Phase.reuse, Phase.generate),
)
def test_all_inline_xlines_have_a_trace_index(dset):
    fh = io.BytesIO()
    write_segy(fh, dset)
    fh.seek(0)
    reader = create_reader(fh, dimensionality=3)
    for num in reader.inline_xline_numbers():
        assert reader.has_trace_index(num)


@given(diagonal_dataset_3d(valid_line_catalog=True))
@settings(
    max_examples=10,
    suppress_health_check=(HealthCheck.too_slow,),
    deadline=None,
    phases=(Phase.explicit, Phase.reuse, Phase.generate),
)
def test_inline_xlines_map_to_correct_trace_index(dset):
    fh = io.BytesIO()
    write_segy(fh, dset)
    fh.seek(0)
    reader = create_reader(fh, dimensionality=3)
    for num in reader.inline_xline_numbers():
        assert reader.trace_index(num) == num[0]
        assert reader.trace_index(num) == num[1]
