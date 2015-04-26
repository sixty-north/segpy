from collections import OrderedDict
from weakref import WeakKeyDictionary
from segpy.docstring import docstring_property
from segpy.util import is_magic_name, underscores_to_camelcase, first_sentence, ensure_contains


class FormatMeta(type):
    """A metaclass for header format classes.
    """

    @classmethod
    def __prepare__(mcs, name, bases):
        return OrderedDict()

    def __new__(mcs, name, bases, namespace):

        # TODO: This is a good point to validate that the fields are in order and that the
        # TODO: format specification is valid.  We shouldn't even build the class otherwise.

        namespace['_ordered_field_names'] = tuple(name for name in namespace.keys()
                                                  if not is_magic_name(name))

        for attr_name, attr in namespace.items():

            # This shenanigans is necessary so we can have all the following work is a useful way
            # help(class), help(instance), help(class.property) and help(instance.property)

            # Set the _name attribute of the field instance if it hasn't already been set
            if isinstance(attr, NamedField):
                if attr._name is None:
                    attr._name = attr_name

            # We rename the *class* and set its docstring so help() works usefully
            # when called with a class containing such fields.
            attr_class = attr.__class__
            if issubclass(attr_class, NamedField) and attr_class is not NamedField:
                attr_class.__name__ = underscores_to_camelcase(attr_name)
                attr_class.__doc__ = attr.documentation

        return super().__new__(mcs, name, bases, namespace)


class NamedField:
    """Instances of NamedField can be detected by the NamedDescriptorResolver metaclass."""

    def __init__(self, value_type, offset, default, documentation):
        self._name = None  # Set later by the metaclass
        self._value_type = value_type
        self._offset = int(offset)
        self._default = self._value_type(default)
        self._documentation = str(documentation)

    @property
    def name(self):
        "The field name."
        return self._name

    @property
    def value_type(self):
        "The field value type (e.g. Int32)"
        return self._value_type

    @property
    def offset(self):
        "The offset it bytes from the beginning of the header."
        return self._offset

    @property
    def default(self):
        "The default value of the field. Must be convertible to value_type."
        return self._default

    @property
    def documentation(self):
        "A descriptive text string."
        return self._documentation

    @docstring_property(__doc__)
    def __doc__(self):
        return first_sentence(self._documentation)

    # TODO: Uncomment this to get HELP
    # def __repr__(self):
    #     return first_sentence(self._documentation)

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)


def field(value_type, offset, default, documentation):
    """
    Args:
        value_type: The type of the field (e.g. Int32)

        offset: The offset in bytes for this field from the start of the header.

        default: The default value for this field.

        documentation: A docstring for the field. The first sentence should be usable
            as a brief description.

    Returns:
        An instance of a subclass of NamedField class.
    """

    # Create a class specifically for this field. This class will later get
    # renamed when the NamedDescriptorMangler metaclass does its job, to
    # a class name based on the field name.

    class SpecificField(NamedField):
        pass

    return SpecificField(value_type, offset, default, documentation)


class ValueField:

    def __init__(self, name, value_type, default, documentation):
        self._name = name
        self._value_type = value_type
        self._default = default
        self._documentation = documentation
        self._instance_data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        if owner is None:
            return self
        if instance not in self._instance_data:
            return self._default
        return self._instance_data[instance]

    def __set__(self, instance, value):
        try:
            self._instance_data[instance] = self._value_type(value)
        except ValueError as e:
            raise ValueError("Assigned value {!r} for {} attribute must be convertible to {}: {}"
                             .format(value, self._name, self._value_type.__name__, e)) from e

    def __delete__(self, instance):
        raise AttributeError("Can't delete {} attribute".format(self._name))

    @docstring_property(__doc__)
    def __doc__(self):
        return self._documentation

    # TODO: Get documentation of these descriptors working correctly


class BuildFromFormat(type):
    """A metaclass for building a data transfer object from a format definition."""

    def __new__(mcs, name, bases, namespace, format_class):
        """Create a new DTO class from a format class."""
        if format_class.__class__ is not FormatMeta:
            raise TypeError("Format class {} specified for class {} does not use the FormatMeta metaclass"
                            .format(format_class.__name__, name))

        bases = ensure_contains(bases, HeaderBase)

        namespace['_format'] = format_class

        for field_name in format_class._ordered_field_names:
            format_field = getattr(format_class, field_name)
            namespace[field_name] = ValueField(
                name=field_name,
                value_type=format_field.value_type,
                default=format_field.default,
                documentation=format_field.documentation)

        return super().__new__(mcs, name, bases, namespace)

    def __init__(mcs, name, bases, namespace, format_class):
        super().__init__(mcs, name, bases)
        pass


class HeaderBase:

    def __init__(self, **kwargs):
        for keyword, value in kwargs.items():
            setattr(self, keyword, value)

    def __repr__(self):
        field_names = self._format._ordered_field_names
        return '{}({})'.format(self.__class__.__name__,
                               ', '.join('{}={}'.format(name, getattr(self, name)) for name in field_names))