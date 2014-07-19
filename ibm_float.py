import struct

def ibm2ieee2(ibm_float):
    """
    ibm2ieee2(ibm_float)
    Used by permission
    (C) Secchi Angelo
    with thanks to Howard Lightstone and Anton Vredegoor.
    """
    dividend = float(16 ** 6)

    if ibm_float == 0:
        return 0.0
    istic, a, b, c = struct.unpack('>BBBB', ibm_float)
    if istic >= 128:
        sign= -1.0
        istic -= 128
    else:
        sign = 1.0
    mant= float(a << 16) + float(b << 8) + float(c)
    return sign * 16 ** (istic - 64) * (mant / dividend)
