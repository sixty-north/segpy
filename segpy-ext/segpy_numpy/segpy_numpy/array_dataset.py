from abc import abstractmethod, ABCMeta
import numpy
from segpy.catalog import CatalogBuilder

from segpy.dataset import Dataset
from segpy.util import identity


class ArrayDataset3d(Dataset):
    """A Dataset where the traces are stored in a NumpyArray.

    """

    def __init__(self,
                 binary_reel_header,
                 textual_reel_header,
                 extended_textual_header,
                 samples,
                 trace_header_template,
                 inline_number_map=identity, # TODO: What about one-based indexing. Should we also have a one_based
                 xline_number_map=identity,  # TODO: which maps zero in the array to one in the SEG Y
                 sample_number_map=identity,
                 complete=True,
                 null=None):
        """
        Args:
            binary_reel_header:

            textual_reel_header:

            extended_textual_header:

            samples: A three dimensional numpy array of samples.

            trace_header_template: A trace header from which trace-invariant
                field values will be copied to generate the trace header
                corresponding to each trace. TODO: Should this be a
                trace-header containing functions?

            inline_number_map: A function mapping array index to inline
                number.

            xline_number_map: A function mapping array index to crossline
                number.

            sample_number_map: A function mapping array index to sample
                number.

            complete (bool): If True, all traces and samples will be
                included in the data set. If false, traces which are
                entirely consist of null or masked samples will be
                excluded.

            null: An optional null value for samples. Any samples which
                are equal to this null value will be treated as null.
                Traces which consist only of null samples will be
                excluded from the data set if 'complete' is False.
                When 'complete' is True and samples is a masked array,
                any masked values will be presented in the dataset as
                being on the null value.
        """
        # TODO: Validate
        self._binary_reel_header = binary_reel_header
        self._textual_reel_header = textual_reel_header
        self._extended_textual_header = extended_textual_header
        self._samples = samples
        self._trace_header_template = trace_header_template
        self._inline_number_map = inline_number_map
        self._xline_number_map = xline_number_map
        self._sample_number_map = sample_number_map
        self._masking_strategy = MaskedSamplesStrategy(self, null) if hasattr(samples, 'mask') else NulledSampleStrategy(self, null)
        self._completion_strategy = CompleteStrategy(self) if complete else IncompleteStrategy(self)

    @property
    def binary_reel_header(self):
        return self._binary_reel_header

    @property
    def textual_reel_header(self):
        return self._textual_reel_header

    @property
    def extended_textual_header(self):
        return self._extended_textual_header

    @property
    def dimensionality(self):
        return 3

    @property
    def samples(self):
        # TODO: Read-only view?
        return self._samples

    def trace_indexes(self):
        return self._completion_strategy.trace_indexes()

    def trace_header(self, trace_index):
        pass

    def trace_samples(self, trace_index, **kwargs):
        self._completion_strategy.inline_xline_index(trace_index)

    def __repr__(self):
        # TODO: More details
        return "{}()".format(self.__class__.__name__)


class NullSampleStrategy(metaclass=ABCMeta):

    def __init__(self, array_dataset, null):
        self._array_dataset = array_dataset
        self._null = null

    @abstractmethod
    def trace_has_samples(self, trace):
        raise NotImplementedError


class NulledSampleStrategy(NullSampleStrategy):

    def __init__(self, array_dataset, null):
        super().__init__(array_dataset, null)

    def trace_has_samples(self, trace):
        return numpy.any(trace != self._null)


class MaskedSamplesStrategy(NullSampleStrategy):

    def __init__(self, array_dataset, null):
        super().__init__(array_dataset, null)

    def trace_has_samples(self, trace):
        mask = trace.mask
        return not mask.all()


class CompletionStrategy(metaclass=ABCMeta):

    def __init__(self, array_dataset):
        self._array_dataset = array_dataset

    @abstractmethod
    def trace_indexes(self):
        raise NotImplementedError

    @abstractmethod
    def inline_xline_index(self, trace_index):
        raise NotImplementedError


class IncompleteStrategy(CompletionStrategy):

    def __init__(self, array_dataset):
        super().__init__(array_dataset)
        self._trace_index_catalog = None

    def trace_indexes(self):
        if self._trace_index_catalog is None:
            trace_index_catalog_builder = CatalogBuilder()
            trace_index = 0
            dataset = self._array_dataset
            samples = dataset._samples
            for inline_index in range(0, samples.shape[0]):
                for xline_index in range(0, samples.shape[1]):
                    trace_samples = samples[inline_index, xline_index, :]
                    if dataset._trace_has_samples(trace_samples):
                        trace_index_catalog_builder.add(trace_index, (inline_index, xline_index))
            self._trace_index_catalog = trace_index_catalog_builder.create()
        return self._trace_index_catalog.keys()

    def inline_xline_index(self, trace_index):
        """Given a trace index, return the 2d index of the trace in the array."""
        try:
            return self._trace_index_catalog[trace_index]
        except KeyError as e:
            raise ValueError("Trace index {} not present in {}".format(trace_index, self._array_dataset))


class CompleteStrategy(CompletionStrategy):

    def __init__(self, array_dataset):
        super().__init__(array_dataset)
        self._trace_indexes = None

    def trace_indexes(self):
        if self._trace_indexes is None:
            samples = self._array_dataset._samples
            self._trace_indexes = range(0, samples.shape[0] * samples.shape[1])
        return self._trace_indexes

    def inline_xline_index(self, trace_index):
        samples = self._array_dataset._samples
        inline_index, xline_index = divmod(trace_index, samples.shape[0])
        if not ((0 <= inline_index < samples.shape[0]) and (0 <= xline_index < samples.shape[1])):
            raise ValueError("Trace index {} not present in {}".format(trace_index, self._array_dataset))
        return inline_index, xline_index

