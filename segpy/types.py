class Int16(int):

    MINIMUM = -32768
    MAXIMUM = 32767
    SIZE = 2
    SEG_Y_TYPE = 'int16'

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls, *args, **kwargs)
        if not (Int16.MINIMUM <= instance <= Int16.MAXIMUM):
            raise ValueError("{} value {!r} outside range {} to {}".format(cls.__name__, instance,
                                                                        cls.MINIMUM, cls.MAXIMUM))
        return instance


class Int32(int):

    MINIMUM = -2147483648
    MAXIMUM = 2147483647
    SIZE = 4
    SEG_Y_TYPE = 'int32'

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls, *args, **kwargs)
        if not (Int32.MINIMUM <= instance <= Int32.MAXIMUM):
            raise ValueError("{} value {!r} outside range {} to {}".format(cls.__name__, instance,
                                                                        cls.MINIMUM, cls.MAXIMUM))
        return instance

