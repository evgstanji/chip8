import pytest

from chip8.chip8 import Chip8

def test_add_wraps_to_one_byte() -> None:
    ch8 = Chip8()
    ch8.V[0] = 0xF0
    ch8.execute(ch8.decode(0x7020))
    assert ch8.V[0] == 0x10
    
def test_clear_screen_in_place() -> None:
    ch8 = Chip8()
    screen = ch8.display
    screen[5] = 1
    ch8.execute(ch8.decode(0x00E0))
    assert ch8.display is screen
    assert not any(screen)