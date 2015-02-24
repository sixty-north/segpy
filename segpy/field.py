from weakref import WeakKeyDictionary

from segpy.docstring import docstring_property
from segpy.util import underscores_to_camelcase


# class FieldItems(object):
#
#     def __init__(self, field):
#         self._field = field
#         self.__doc__ = field.__doc__
#
#     @property
#     def name(self):
#         if self._field._name is not None:
#             return self._field._name
#         raise AttributeError("Field is unnamed")
#
#     @property
#     def ftype(self):
#         return self._field._field_type
#
#     @property
#     def value(self):
#         return self._value if hasattr(self, '_value') else self._field._default
#
#     @value.setter
#     def value(self, value):
#         self._value = self._field._field_type(value)
#
#     @property
#     def default(self):
#         return self._field._default
#
#     @property
#     def offset(self):
#         return self._start_offset if hasattr(self, '_start_offset') else self._field._offset
#
#     @docstring_property
#     def __doc__(self):
#         return self._field._documentation


# class Field(object):
#     """A field of a binary format, specifying type, file offset, value and default.
#
#     Attributes:
#         name: The name of the field
#         ftype: The type of the field.
#         value: The value of the field.
#         offset: The byte offset of the start of the field.
#         default: The default value of the field.
#         __doc__: The documentation of the field.
#     """
#
#     def __init__(self, field_type, offset, default, documentation):
#         self._name = None  # This field can be set by the NamedDescriptorResolverMetaClass
#         self._field_type = field_type
#         self._offset = offset
#         self._default = default
#         self._data = WeakKeyDictionary()
#         self._documentation = documentation
#
#     def __get__(self, instance, owner):
#         if instance is None:
#             return self
#         return self._data.setdefault(instance, FieldItems(self))
#
#     def __set__(self, instance, value):
#         raise AttributeError("Can't set field attribute. Did you intend to set field.value instead?")
#
#     def __delete__(self, instance):
#         raise AttributeError("Can't delete field attribute. Did you intend to set field.value instead?")


# def field(field_type, offset, default, documentation):
#
#     class SpecificField(Field):
#         pass
#
#     SpecificField.__doc__ = documentation
#
#     """Declare a field descriptor.
#
#     Args:
#         field_type: The type of the field.
#         offset: The offset in bytes of this field in a binary stream.
#         default: The default value of this field.
#         documentation: Description of the field.
#
#     Returns:
#         A Field descriptor.
#     """
#
#     return SpecificField(field_type, offset, default, documentation)


class MetaField(object):

    def __init__(self, field_type, offset, default, documentation):
        self._field_type = field_type
        self._offset = offset
        self._default = default
        self._documentation = documentation

    @property
    def field_type(self):
        return self._field_type

    @property
    def offset(self):
        return self._offset

    @property
    def default(self):
        return self._default

    @property
    def documentation(self):
        return self._documentation


def field(field_type, offset, default, documentation):
    return MetaField(field_type, offset, default, documentation)


# class NamedDescriptorResolver(type):
#     """A metaclass for assigning descriptor names.
#     """
#     def __new__(cls, class_name, bases, class_dict):
#         for name, attr in class_dict.items():
#             attr_class = attr.__class__
#             if issubclass(attr_class, Field) and attr_class is not Field:
#                 attr_class.__name__ = underscores_to_camelcase(name)
#         return type.__new__(cls, class_name, bases, class_dict)


class FormatFieldItems(object):

    def __init__(self, field):
        self._field = field
        self.__doc__ = field.__doc__

    @property
    def ftype(self):
        return self._field._field_type

    @property
    def offset(self):
        return self._field._offset

    @docstring_property
    def __doc__(self):
        return self._field._documentation


class FormatField(object):
    """A field of a binary format, specifying type, file offset, value and default.

    Attributes:
        name: The name of the field
        ftype: The type of the field.
        offset: The byte offset of the start of the field.
        __doc__: The documentation of the field.
    """

    def __init__(self, field_type, offset, documentation):
        self._name = None  # This field can be set by the NamedDescriptorResolver
        self._field_type = field_type
        self._offset = offset
        self._data = WeakKeyDictionary()
        self._documentation = documentation

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self._data.setdefault(instance, FormatFieldItems(self))

    def __set__(self, instance, value):
        raise AttributeError("Can't set field attribute. Did you intend to set field.value instead?")

    def __delete__(self, instance):
        raise AttributeError("Can't delete field attribute. Did you intend to set field.value instead?")



def binary_format(header_definition):

    class BinaryFormat(type):
        """A metaclass for specifying the field type."""

        def __new__(cls, class_name, bases, class_dict):
            for name in class_dict:
                print("Found field : {}".format(name))
                attr = class_dict[name]
                if isinstance(attr, MetaField):
                    print("Found meta field : {}".format(attr))
                    meta_field = class_dict[name]
                    class_dict[name] = FormatField(field_type=meta_field.ftype,
                                                   offset=meta_field.offset,
                                                   documentation=meta_field.doc)
            return type.__new__(cls, class_name, bases, class_dict)
