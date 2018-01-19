import enum
from .datatypes import LIMITS, SEG_Y_TYPE_TO_CTYPE, size_in_bytes


class IntFieldMeta(type):
    """Metaclass for signed and unsigned int fields.
    """

    def class_new(cls, *args, **kwargs):
        instance = super(cls, cls).__new__(cls, *args, **kwargs)
        if not (cls.MINIMUM <= instance <= cls.MAXIMUM):
            raise ValueError("{} value {!r} outside range {} to {}".format(
                cls.__name__, instance,
                cls.MINIMUM, cls.MAXIMUM))
        return instance

    def __new__(cls, name, bases, namespace,
                seg_y_type,
                min_value=None,
                max_value=None,
                **kwargs):

        bases = bases + ((int,) if int not in bases else ())

        if min_value is None:
            min_value = LIMITS[seg_y_type].min

        if max_value is None:
            max_value = LIMITS[seg_y_type].max

        namespace.update({
            'SEG_Y_TYPE': seg_y_type,
            'MINIMUM': min_value,
            'MAXIMUM': max_value,
            'SIZE': size_in_bytes(SEG_Y_TYPE_TO_CTYPE[seg_y_type]),
            '__new__': cls.class_new,
        })
        return super().__new__(cls, name, bases, namespace, **kwargs)

    def __init__(cls, name, bases, namespace, *args, **kwargs):
        super().__init__(name, bases, namespace)


class Int16(int,
            metaclass=IntFieldMeta,
            seg_y_type='int16'):
    """16-bit signed integer."""
    pass


class NNInt16(int,
              metaclass=IntFieldMeta,
              seg_y_type='nnint16'):
    """Non-negative 16-bit signed integer."""
    pass


class Int32(int,
            metaclass=IntFieldMeta,
            seg_y_type='int32'):
    """32-bit signed integer."""
    pass


class NNInt32(int,
              metaclass=IntFieldMeta,
              seg_y_type='nnint32'):
    """Non-negative 32-bit signed integer."""
    pass


class IntEnumFieldMeta(IntFieldMeta):
    """Metaclass for fields which are defined by an `enum.IntEnum`.
    """

    def class_new(cls, *args, **kwargs):
        instance = super(cls, cls).__new__(cls, *args, **kwargs)
        return cls.ENUM(instance)

    def __new__(cls, name, bases, namespace, enum, seg_y_type='int16', **kwargs):
        if any((value < LIMITS[seg_y_type].min)
               or (value > LIMITS[seg_y_type].max)
               for value in enum):
            raise ValueError(
                'Enum values must be within specified SEGY field type range.')

        namespace['ENUM'] = enum

        return super().__new__(cls, name, bases, namespace, seg_y_type, **kwargs)

    def __init__(cls, name, bases, namespace, *args, **kwargs):
        super().__init__(name, bases, namespace)
