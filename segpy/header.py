from collections import OrderedDict
from weakref import WeakKeyDictionary
from itertools import chain

from segpy import __version__
from segpy.util import underscores_to_camelcase, super_class, collect_attributes


class BaseHeader:
    """An abstract base class for header format definitions.

    Prefer to inherit from Header rather than BaseHeader.
    """

    def __init__(self, *args, **kwargs):
        """Initialise a header instance.

        Args:
            *args: Positional arguments are matched with header fields in the order they
                are declared in the class definition (i.e. the same order defined by
                the ordered_field_names() method.  From a performance perspective
                positional arguments are faster than keyword arguments.

            **kwargs: Keyword arguments are assigned to the header field of the same name.
                Keyword argument values will overwrite any positional argument values.

        Raises:
            TypeError: If keyword argument names do not correspond to header fields.
        """
        for keyword, arg in zip(self.ordered_field_names(), args):
            setattr(self, keyword, arg)

        for keyword, arg in kwargs.items():
            try:
                getattr(self, keyword)
            except AttributeError as e:
                raise TypeError("{!r} is not a recognised field name for {!r}"
                                .format(keyword, self.__class__.__name__)) from e
            else:
                setattr(self, keyword, arg)

    _ordered_field_names = tuple()

    @classmethod
    def ordered_field_names(cls):
        """The ordered list of field names.

        This is a metamethod which should be called on cls.

        Returns:
            An tuple containing the field names in order.
        """

        if cls is BaseHeader:
            return cls._ordered_field_names
        return super_class(cls).ordered_field_names() + cls._ordered_field_names

    def copy(self, **updates):
        fields = {name: getattr(self, name) for name in self.ordered_field_names()}
        fields.update(updates)
        obj = type(self)(**fields)
        return obj

    def __copy__(self):
        return self.copy()

    def __getattr__(self, name):
        raise AttributeError("Object of type {!r} has no attribute {!r}".format(self.__class__.__name__, name))

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ', '.join("{}={}".format(k, getattr(self, k)) for k in self.ordered_field_names()))

    def __getstate__(self):
        state = self.__dict__.copy()
        state['__version__'] = __version__
        state['_all_attributes'] = OrderedDict((name, getattr(self, name)) for name in self._ordered_field_names)
        return state

    def __setstate__(self, state):
        if state['__version__'] != __version__:
            raise TypeError("Cannot unpickle {} version {} into version {}"
                            .format(self.__class__.__name__,
                                    state['__version__'],
                                    __version__))
        del state['__version__']

        for name, value in state['_all_attributes'].items():
            setattr(self, name, value)
        del state['_all_attributes']
        self.__dict__.update(state)


def are_equal(header_a, header_b):
    """Compare two headers for equality.

    Note:
        This is not implemented as __eq__() to prevent recursive behaviour in the header descriptor.
    """
    if type(header_a) != type(header_b):
        return False
    return all(getattr(header_a, field_name) == getattr(header_b, field_name) for field_name in header_a.ordered_field_names())


class FormatMeta(type):
    """A metaclass for header format classes.
    """

    @classmethod
    def __prepare__(mcs, name, bases, *args, **kwargs):
        return OrderedDict()

    def __new__(mcs, name, bases, namespace):

        # TODO: This is a good point to validate that the fields are in order and that the
        # TODO: format specification is valid.  We shouldn't even build the class otherwise.

        # TODO: Also validate existence of LENGTH_IN_BYTES

        namespace['_ordered_field_names'] = tuple(name for name, attr in namespace.items()
                                                  if isinstance(attr, HeaderFieldDescriptor))

        transitive_bases = set(chain.from_iterable(type(base).mro(base) for base in bases))

        if BaseHeader not in transitive_bases:
            bases = (BaseHeader,) + bases

        for attr_name, attr in namespace.items():

            # This shenanigans is necessary so we can have all the following work is a useful way
            # help(class), help(instance), help(class.property) and help(instance.property)

            # Set the _name attribute of the field instance if it hasn't already been set
            if isinstance(attr, HeaderFieldDescriptor):
                if attr._name is None:
                    attr._name = attr_name

        return super().__new__(mcs, name, bases, namespace)


def is_public_non_field_attr(name, attr):
    return ((not name.startswith('_'))
            and (not isinstance(attr, HeaderFieldDescriptor)
                 and (not isinstance(attr, classmethod))))


class SubFormatMeta(FormatMeta):
    """A metaclass for a format class which has a subset of the fields in an existing format class.

    SubFormat classes can be used to reduce storage requirements and increase performance, since they can be
    used to generate simpler HeaderPackers.

    Usage:

        class MySubFormat(metaclass=SubFormatMeta,
                          parent_format=MyFormatClass,
                          parent_field_names=[
                             'first_field_name',
                             'second_field_name']):
            pass
    """

    def __new__(mcs, name, bases, namespace, parent_format, parent_field_names):
        """
        Args:
            name: The name of the actual class being created by this metaclass.
            bases: The base classes of the actual class.
            parent_format: An existing Format (?Header) on which (sort out terminology here)
                of which this format has a subset of fields.
            parent_field_names: An iterable series of field names which this format should
                duplicate from the parent_format.
        """

        # Copy the requested fields, by creating a new descriptor based
        # on information retrieved from the existing descriptor
        for field_name in parent_field_names:
            named_field = getattr(parent_format, field_name)
            assert named_field.name == field_name
            field_copy = field(named_field.value_type,
                               named_field.offset,
                               named_field.default,
                               named_field.documentation)
            namespace[field_name] = field_copy

        # Copy other non-field class attributes
        non_field_attributes = list(collect_attributes(parent_format, BaseHeader, is_public_non_field_attr))
        namespace.update((name, value) for _, name, value in non_field_attributes)

        # Add a reference back to the original format
        namespace['_parent_format'] = parent_format

        return super().__new__(mcs, name, bases, namespace)

    def __init__(mcs, name, bases, namespace, parent_format, parent_field_names):
        # Absorb the additional arguments
        super().__init__(name, bases, namespace)


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
        "The offset in bytes from the beginning of the header."
        return self._offset

    @property
    def default(self):
        "The default value of the field. Must be convertible to value_type."
        return self._default

    @property
    def documentation(self):
        "A descriptive text string."
        return self._documentation

    def __repr__(self):
        return "{}(name={!r}, value_type={!r}, offset={!r}, default={!r})".format(
            self.__class__.__name__,
            self.name,
            self.value_type.__name__,
            self.offset,
            self.default)


def field(value_type, offset, default, documentation):
    """
    Args:
        value_type: The type of the field (e.g. Int32)

        offset: The offset in bytes for this field from the start of the header.

        default: The default value for this field.

        documentation: A docstring for the field. The first sentence should be usable
            as a brief description.

    Returns:
        An instance of a subclass of HeaderFieldDescriptor class.
    """
    return HeaderFieldDescriptor(value_type, offset, default, documentation)


class HeaderFieldDescriptor:

    def __init__(self, value_type, offset, default, documentation):
        SpecificNamedField = type('SpecificNamedField', (NamedField,), {'__doc__': documentation})
        self._named_field = SpecificNamedField(value_type, offset, default, documentation)
        self._instance_data = WeakKeyDictionary()

    @property
    def _name(self):
        return self._named_field.name

    @_name.setter
    def _name(self, value):
        self._named_field.__class__.__name__ = underscores_to_camelcase(value + '_field')
        self._named_field._name = value

    def __get__(self, instance, owner):
        """Retrieve the format or instance data.

        When called on the class we return a NamedField instance containing the format data. For example:

            line_seq_num_default = TraceHeaderRev1.line_sequence_num.default
            line_seq_num_offset = TraceHeaderRev1.line_sequence_num.offset

        When called on an instance we return the field value.

            line_seq_num = my_trace_header.line_sequence_num
        """
        if instance is None:
            return self._named_field
        if instance not in self._instance_data:
            return self._named_field.default
        return self._instance_data[instance]

    def __set__(self, instance, value):
        """Set the field value."""
        try:
            self._instance_data[instance] = self._named_field._value_type(value)
        except ValueError as e:
            raise ValueError("Assigned value {!r} for {} attribute must be convertible to {}: {}"
                             .format(value, self._name, self._named_field._value_type.__name__, e)) from e

    def __delete__(self, instance):
        raise AttributeError("Can't delete {} attribute".format(self._name))


class Header(BaseHeader, metaclass=FormatMeta):
    """A base class for header definition classes."""
    pass
