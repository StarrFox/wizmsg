from hypothesis import given
from hypothesis.strategies import integers, booleans, floats

from wizmsg import ByteInterface


@given(booleans())
def test_bool(test_value):
    interface = ByteInterface()

    interface.write_bool(test_value)
    interface.seek(0)

    assert interface.bool() == test_value


# nan doesn't work with ==, nan is however written and read correctly
@given(floats(width=32, allow_nan=False))
def test_float(test_value):
    interface = ByteInterface()

    interface.write_float(test_value)
    interface.seek(0)

    assert interface.float() == test_value


@given(floats(allow_nan=False))
def test_double(test_value):
    interface = ByteInterface()

    interface.write_double(test_value)
    interface.seek(0)

    assert interface.double() == test_value


@given(integers(0, 0xFF))
def test_unsigned1(test_value):
    interface = ByteInterface()

    interface.write_unsigned1(test_value)
    interface.seek(0)

    assert interface.unsigned1() == test_value


@given(integers(-0x7F - 1, 0x7F))
def test_signed1(test_value):
    interface = ByteInterface()

    interface.write_signed1(test_value)
    interface.seek(0)

    assert interface.signed1() == test_value


@given(integers(0, 0xFFFF))
def test_unsigned2(test_value):
    interface = ByteInterface()

    interface.write_unsigned2(test_value)
    interface.seek(0)

    assert interface.unsigned2() == test_value


@given(integers(-0x7FFF - 1, 0x7FFF))
def test_signed2(test_value):
    interface = ByteInterface()

    interface.write_signed2(test_value)
    interface.seek(0)

    assert interface.signed2() == test_value


@given(integers(0, 0xFFFFFFFF))
def test_unsigned4(test_value):
    interface = ByteInterface()

    interface.write_unsigned4(test_value)
    interface.seek(0)

    assert interface.unsigned4() == test_value


@given(integers(-0x7FFFFFFF - 1, 0x7FFFFFFF))
def test_signed4(test_value):
    interface = ByteInterface()

    interface.write_signed4(test_value)
    interface.seek(0)

    assert interface.signed4() == test_value


@given(integers(0, 0xFFFFFFFFFFFFFFFF))
def test_unsigned8(test_value):
    interface = ByteInterface()

    interface.write_unsigned8(test_value)
    interface.seek(0)

    assert interface.unsigned8() == test_value


@given(integers(-0x7FFFFFFFFFFFFFFF - 1, 0x7FFFFFFFFFFFFFFF))
def test_signed4(test_value):
    interface = ByteInterface()

    interface.write_signed8(test_value)
    interface.seek(0)

    assert interface.signed8() == test_value
