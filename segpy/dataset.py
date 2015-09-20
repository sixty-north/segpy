from abc import ABCMeta, abstractmethod


class Dataset(metaclass=ABCMeta):

    @property
    @abstractmethod
    def textual_reel_header(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def binary_reel_header(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def extended_textual_header(self):
        raise NotImplementedError

    @property
    def dimensionality(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def trace_indexes(self):
        raise NotImplementedError

    @abstractmethod
    def trace_header(self, trace_index):
        raise NotImplementedError

    @abstractmethod
    def trace_samples(self, trace_index):
        raise NotImplementedError

