from contextlib import contextmanager
import segpy.ibm_float_packer


@contextmanager
def force_python_ibm_float(force):
    """Configure segpy to run with and without the C++ implementation of IBM
    floating point un/packing.
    """
    orig = segpy.ibm_float_packer.force_python_ibm_floats
    segpy.ibm_float_packer.force_python_ibm_floats = force
    try:
        yield force
    finally:
        segpy.ibm_float_packer.force_python_ibm_floats = orig
