from segpy.dataset import Dataset


class ArrayDataset3d(Dataset):
    """A Dataset where the traces are stored in a NumpyArray
    """

    def trace_header(self, trace_index):
        pass

    # TODO: If all exposed data is Unicode, this doesn't belong here
    def encoding(self):
        pass

    def binary_reel_header(self):
        pass

    def trace_indexes(self):
        pass

    def extended_textual_header(self):
        pass

    def textual_reel_header(self):
        pass

    # Is any of the internal data endian-specific?  Does this belong here?
    def endian(self):
        pass

    def trace_samples(self, trace_index):
        pass
