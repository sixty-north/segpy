import pytest
import test.util


@pytest.fixture(params=[True, False])
def ibm_floating_point_impls(request):
    """Configure segpy to run with and without the C++ implementation of IBM
    floating point un/packing.
    """
    with test.util.force_python_ibm_float(request.param) as force:
        yield force
