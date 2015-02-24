class Int16(int):

    MINIMUM = -32768
    MAXIMUM = 32767
    SIZE = 2

    def __new__(cls, *args, **kwargs):
        instance = super(cls).__new__(cls, *args, **kwargs)
        if not (Int16.MINIMUM <= instance <= Int16.MAXIMUM):
            raise ValueError("{} value {!r} outside range {}–{}".format(cls.__name__, instance,
                                                                        cls.MINIMUM, cls.MAXIMUM))
        return instance

class Int32(int):

    MINIMUM = -2147483648
    MAXIMUM = 2147483647
    SIZE = 4

    def __new__(cls, *args, **kwargs):
        instance = super(Int32, cls).__new__(cls, *args, **kwargs)
        if not (Int16.MINIMUM <= instance <= Int16.MAXIMUM):
            raise ValueError("{} value {!r} outside range {}–{}".format(cls.__name__, instance,
                                                                        cls.MINIMUM, cls.MAXIMUM))
        return instance

