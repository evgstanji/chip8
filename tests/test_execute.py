from chip8.chip8 import Chip8
import pytest

def test_add_wraps_to_one_byte() -> None:
    ch8 = Chip8()
    ch8.V[0] = 0xF0
    ch8.execute(ch8.decode(0x7020))
    assert ch8.V[0] == 0x10