from weakref import WeakKeyDictionary

from segpy.util import underscores_to_camelcase, first_sentence, lower_first, UNSET


def field_mangler(descriptor):
    """A factory function for creating a metaclass which detects descriptors which subclass a certain archetype.

    Args:
        descriptor: The type (class) of a descriptor used to identity descriptor instances which should be renamed.
    """

    class NamedDescriptorMangler(type):
        """A metaclass for assigning descriptor names.
        """
        def __new__(mcs, class_name, bases, class_dict):
            for name, attr in class_dict.items():

                # This shenanigans is necessary so we can have all the following work is a useful way
                # help(class), help(instance), help(class.property) and help(instance.property)

                # Set the _name attribute of the field instance if it hasn't already been set
                if isinstance(attr, descriptor):
                    if attr._name is None:
                        attr._name = name

                # We rename the *class* and set its docstring so help() works usefully
                # when called with a class containing such fields.
                attr_class = attr.__class__
                if issubclass(attr_class, descriptor) and attr_class is not descriptor:
                    attr_class.__name__ = underscores_to_camelcase(name)
                    attr_class.__doc__ = attr.assemble_docstring()

            return super(NamedDescriptorMangler, mcs).__new__(mcs, class_name, bases, class_dict)

    return NamedDescriptorMangler


class NamedField(object):
    """Instances of NamedField can be detected by the NamedDescriptorResolver metaclass."""

    def __init__(self, docstrings=None):
        # These fields can be set by the NamedDescriptorResolver metaclass
        self._name = None
        self._docstrings = docstrings

    def assemble_docstring(self):
        if self._name is None:
            raise RuntimeError("Field name is not set.")
        return first_sentence(self._docstrings.get(self._name, '<unknown-field>'))

# ----------------------------------------------------------------------------------------------------------------------

class BinaryField(object):
    """Aggregates the name, type and offset of a field within a binary format.
    """

    def __init__(self, field):
        self._field = field

    @property
    def name(self):
        """The field name (read-only)."""
        if self._field._name is not None:
            return self._field._name
        raise AttributeError("Field is unnamed")

    @property
    def ftype(self):
        """The type of the field described using the classes in segpy.types"""
        return self._field._field_type

    @property
    def offset(self):
        """The one-based (IMPORTANT!) offset in bytes of the field from the beginning of the structure"""
        return self._field._offset


class BinaryFieldDescriptor(NamedField):
    """A field of a binary format, specifying type, file offset, value and default.

    Attributes:
        ftype: The type of the field.
        offset: The byte offset of the start of the field.
    """

    def __init__(self, ftype, offset, docstrings):
        super(BinaryFieldDescriptor, self).__init__(docstrings)
        self._ftype = ftype
        self._offset = offset
        self._data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self._data.setdefault(instance, BinaryField(self))

    def __set__(self, instance, value):
        raise AttributeError("Can't set binary field attribute. Did you intend to set field.ftype or field.offset instead?")

    def __delete__(self, instance):
        raise AttributeError("Can't delete field attribute. Did you intend to set field.ftype or field.offset instead?")

    def assemble_docstring(self):
        if self._name is None:
            raise RuntimeError("Field name is not set.")
        return "A BinaryField containing the type and byte offset for the {}".format(
            first_sentence(lower_first(self._docstrings.get(self._name, '<unknown-field>'))))


#-----------------------------------------------------------------------------------------------------------------------


class ValueField(object):
    """Aggregates the name, type and offset of a field within a binary format.
    """

    def __init__(self, field):
        self._field = field
        self._value = UNSET

    @property
    def name(self):
        """The field name (read-only)."""
        if self._field._name is not None:
            return self._field._name
        raise AttributeError("Field is unnamed")

    @property
    def default(self):
        return self._field._default

    @property
    def value(self):
        """The type of the field described using the classes in segpy.types"""
        return self._value if self._value is not UNSET else self.default

    @value.setter
    def value(self, v):
        self._value = v


class ValueFieldDescriptor(NamedField):
    """A field of a binary format, specifying type, file offset, value and default.

    Attributes:
        value: The value of the field.
    """

    def __init__(self, default, docstrings):
        super(ValueFieldDescriptor, self).__init__(docstrings)
        self._default = default
        self._data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self._data.setdefault(instance, ValueField(self))

    def __set__(self, instance, value):
        raise AttributeError("Can't set field attribute. Did you intend to set field.value instead?")

    def __delete__(self, instance):
        raise AttributeError("Can't delete field attribute. Did you intend to set field.value instead?")

    def assemble_docstring(self):
        if self._name is None:
            raise RuntimeError("Field name is not set.")
        return "A ValueField containing the value and default for the {}".format(
            first_sentence(lower_first(self._docstrings.get(self._name, '<unknown-field>'))))

# ----------------------------------------------------------------------------------------------------------------------


def field(descriptor, docstrings, **kwargs):
    """
    Args:
        descriptor: The type (class) of the descriptor be be created.

        docstrings: A dictionary of strings where the docstring for the descriptor can be looked up using the
            descriptor name.  For this to work correctly, the class hosting the descriptors should use a metaclass
            created with field_manger(descriptor). e.g. class Foo(metaclass=field_mangler(descriptor))

        **kwargs: Any other arguments will be forwarded to the descriptor constructor.

    Returns:
        An instance of the descriptor class.
    """

    # Create a class specifically for this field. This class will later get
    # renamed when the NamedDescriptorMangler metaclass does its job, to
    # a class name based on the field name.

    class SpecificField(descriptor):
        pass

    return SpecificField(docstrings=docstrings, **kwargs)