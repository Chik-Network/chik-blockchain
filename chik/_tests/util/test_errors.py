from __future__ import annotations

from chik_rs.sized_ints import int16

from chik.util.errors import Err


def test_error_codes_int16() -> None:
    # Make sure all Err codes fit into int16 because its part of the ProtocolMessageTypes.error message structure
    for err in Err:
        assert int16(err.value) == err.value
