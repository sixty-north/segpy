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

        bases = bases + (int,)

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


class Int16(metaclass=IntFieldMeta,
            seg_y_type='int16'):
    pass


class NNInt16(metaclass=IntFieldMeta,
              seg_y_type='nnint16'):
    pass


class Int32(metaclass=IntFieldMeta,
            seg_y_type='int32'):
    pass


class NNInt32(metaclass=IntFieldMeta,
              seg_y_type='nnint32'):
    pass


class IntEnumFieldMeta(IntFieldMeta):
    """Metaclass for int fields which are limited to a set of values.
    """

    def class_new(cls, *args, **kwargs):
        instance = super(cls, cls).__new__(cls, *args, **kwargs)
        if instance not in cls.VALUES:
            raise ValueError("{} value {!r} not in valid value set {}".format(
                cls.__name__, instance, cls.VALUES))
        return instance

    def __new__(cls, name, bases, namespace, values, seg_y_type='int16', **kwargs):
        if any((value < LIMITS[seg_y_type].min)
               or (value > LIMITS[seg_y_type].max)
               for value in values):
            raise ValueError(
                'Enum values must be within specified SEGY field type range.')

        namespace['VALUES'] = set(values)

        return super().__new__(cls, name, bases, namespace, seg_y_type, **kwargs)

    def __init__(cls, name, bases, namespace, *args, **kwargs):
        super().__init__(name, bases, namespace)
