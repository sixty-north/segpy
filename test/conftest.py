import pytest
import segpy.toolkit as toolkit


@pytest.fixture(params=[True, False])
def ibm_floating_point_impls(request):
    """Configure segpy to run with and without the C++ implementation of IBM
    floating point un/packing.
    """
    orig = toolkit.force_python_ibm_floats
    toolkit.force_python_ibm_floats = request.param
    try:
        yield request.param
    finally:
        toolkit.force_python_ibm_floats = orig
