from contextlib import contextmanager
import segpy.toolkit as toolkit


@contextmanager
def force_python_ibm_float(force):
    """Configure segpy to run with and without the C++ implementation of IBM
    floating point un/packing.
    """
    orig = toolkit.force_python_ibm_floats
    toolkit.force_python_ibm_floats = force
    try:
        yield force
    finally:
        toolkit.force_python_ibm_floats = orig
