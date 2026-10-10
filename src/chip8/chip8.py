from typing import NamedTuple
import random

PROGRAM_START = 0x200
BYTES_PER_LINE = 16
OPCODE_SIZE = 2

# display resolution
HEIGHT = 32
WIDTH = 64

NUMBER_KEYS = 16

FONT_START = 0x050
FONT = bytes([
    0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
    0x20, 0x60, 0x20, 0x20, 0x70,  # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
    0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
    0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
    0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
    0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
    0xF0, 0x80, 0xF0, 0x80, 0x80,  # F
])
BYTES_PER_GLYPH = 5

class Instruction(NamedTuple):
    kind: int
    x: int
    y: int
    n: int
    nn: int
    nnn: int

class Chip8:
    def __init__(self, chip48_mode: bool = False) -> None:

        # shift quirk: CHIP-8 shifts VY into VX, CHIP-48 shifts VX itself
        self.chip48_mode = chip48_mode

        self.display = bytearray(WIDTH * HEIGHT)
        self.memory = bytearray(4096)
        self.memory[FONT_START: FONT_START + len(FONT)] = FONT
        self.PC = PROGRAM_START
        self.V = [0x0] * 16
        self.I = 0x0
        self.stack: list[int] = []
        self.delay_timer: int = 0
        self.sound_timer: int = 0
        self.keys: list[bool] = [False] * NUMBER_KEYS

    def load_rom(self, path: str) -> None:
        with open(path, 'rb') as file:
            data = file.read()
        self.memory[PROGRAM_START: PROGRAM_START + len(data)] = data

    def dump(self, start: int, count: int) -> None:
        for addr in range(start, start + count, BYTES_PER_LINE):
            row = self.memory[addr : addr + BYTES_PER_LINE]
            hex_line = " ".join(f"{byte:02X}" for byte in row)
            print(f"{addr:04X}: {hex_line}")

    def fetch(self) -> int:
        hi = self.memory[self.PC]
        lo = self.memory[self.PC + 1]
        opcode = (hi << 8) | lo
        self.PC += OPCODE_SIZE
        return opcode

    def decode(self, opcode: int) -> Instruction:
        return Instruction(
            kind=(opcode >> 12),
            x=(opcode >> 8) & 0xF,
            y=(opcode >> 4) & 0xF,
            n=opcode & 0xF,
            nn=opcode & 0xFF,
            nnn=opcode & 0xFFF,
        )

    def execute(self, ins: Instruction) -> None:
        match ins.kind:
            case 0x0 if ins.nnn == 0x0E0:
                self.display[:] = bytes(WIDTH * HEIGHT)
            case 0x0 if ins.nnn == 0x0EE:
                self.PC = self.stack.pop()
            case 0x1:
                self.PC = ins.nnn
            case 0x2:
                self.stack.append(self.PC)
                self.PC = ins.nnn
            # 3XNN
            case 0x3:
                if self.V[ins.x] == ins.nn:
                    self.PC += OPCODE_SIZE
            # 4XNN
            case 0x4:
                if self.V[ins.x] != ins.nn:
                    self.PC += OPCODE_SIZE
            # 5XY0
            case 0x5 if ins.n == 0x0:
                if self.V[ins.x] == self.V[ins.y]:
                    self.PC += OPCODE_SIZE
            case 0x6:
                self.V[ins.x] = ins.nn
            case 0x7:
                self.V[ins.x] = (ins.nn + self.V[ins.x]) & 0xFF
            case 0x8:
                self.alu(ins)
            # 9XY0
            case 0x9 if ins.n == 0x0:
                if self.V[ins.x] != self.V[ins.y]:
                    self.PC += OPCODE_SIZE
            case 0xA:
                self.I = ins.nnn
            case 0xB:
                if self.chip48_mode:
                    self.PC = ins.nnn + self.V[ins.x]
                else:
                    self.PC = ins.nnn + self.V[0x0]
                
            # CXNN
            case 0xC:
                self.V[ins.x] = random.randint(0x0, 0xFF) & ins.nn
            # DXYN
            case 0xD:
                x0 = self.V[ins.x] % WIDTH
                y0 = self.V[ins.y] % HEIGHT
                self.V[0xF] = 0
                for row in range(ins.n):
                    sprite_byte = self.memory[self.I + row]
                    for col in range(8):
                        bit = (sprite_byte >> (7 - col)) & 1
                        x = x0 + col
                        y = y0 + row
                        if x >= WIDTH or y >= HEIGHT:
                            continue
                        index = y * WIDTH + x
                        if bit and self.display[index]:
                            self.V[0xF] = 1
                        self.display[index] ^= bit
            case 0xE if ins.nn == 0x9E:
                if self.keys[self.V[ins.x] & 0xF]:
                    self.PC += OPCODE_SIZE
            case 0xE if ins.nn == 0xA1:
                if not self.keys[self.V[ins.x] & 0xF]:
                    self.PC += OPCODE_SIZE
            case 0xF if ins.nn in (0x07, 0x15, 0x18):
                self.timer_ops(ins)
            case 0xF:
                self.memory_ops(ins)
            case _:
                opcode = (ins.kind << 12) | ins.nnn
                raise ValueError(f"Unknown opcode: {opcode:04X}")

    def tick_timers(self) -> None:
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1

    def timer_ops(self, ins: Instruction) -> None:
        match ins.nn:
            case 0x07:
                self.V[ins.x] = self.delay_timer
            case 0x15:
                self.delay_timer = self.V[ins.x]
            case 0x18:
                self.sound_timer = self.V[ins.x]

    def memory_ops(self, ins: Instruction) -> None:
        vx = self.V[ins.x]
        match ins.nn:
            # FX0A "Press any key" instruction
            case 0x0A:
                for key in range(NUMBER_KEYS):
                    if self.keys[key]:
                        self.V[ins.x] = key
                        return
                self.PC -= OPCODE_SIZE
            case 0x1E:
                self.I = (self.I + vx) & 0xFFF
            case 0x29:
                self.I = FONT_START + (vx & 0xF) * BYTES_PER_GLYPH
            case 0x33:
                self.memory[self.I] = vx // 100
                self.memory[self.I + 1] = vx // 10 % 10
                self.memory[self.I + 2] = vx % 10
            case 0x55:
                for i in range(ins.x + 1):
                    self.memory[self.I + i] = self.V[i]
                self.I += ins.x + 1
            case 0x65:
                for i in range(ins.x + 1):
                    self.V[i] = self.memory[self.I + i]
                self.I += ins.x + 1
            case _:
                opcode = (ins.kind << 12) | ins.nnn
                raise ValueError(f"Unknown opcode: {opcode:04X}")

    def alu(self, ins: Instruction) -> None:
        vx, vy = self.V[ins.x], self.V[ins.y]
        flag: int | None = None
        match ins.n:
            case 0x0:
                result = vy
            case 0x1:
                result, flag = vx | vy, 0
            case 0x2:
                result, flag = vx & vy, 0
            case 0x3:
                result, flag = vx ^ vy, 0
            case 0x4:
                total = vx + vy
                result, flag = total & 0xFF, int(total > 0xFF)
            case 0x5:
                total = vx - vy
                result, flag = total & 0xFF, int(vx >= vy)
            case 0x7:
                total = vy - vx
                result, flag = total & 0xFF, int(vy >= vx)
            case 0x6:
                source = vx if self.chip48_mode else vy
                result = source >> 1
                flag = source & 1
            case 0xE:
                source = vx if self.chip48_mode else vy
                result = (source << 1) & 0xFF
                flag = source >> 7
            case _:
                opcode = (ins.kind << 12) | ins.nnn
                raise ValueError(f"Unknown opcode: {opcode:04X}")
        self.V[ins.x] = result
        if flag is not None:
            self.V[0xF] = flag

    def render(self) -> None:
        for y in range(HEIGHT):
            row = self.display[WIDTH * y: (y + 1) * WIDTH]
            print("".join("#" if pixel else " " for pixel in row))

    def run(self, steps: int) -> None:
        for _ in range(steps):
            opcode = self.fetch()
            instruction = self.decode(opcode)
            self.execute(instruction)

def main() -> None:
    ch8 = Chip8()
    ch8.load_rom("./roms/Particle Demo [zeroZshadow, 2008].ch8")
    ch8.dump(ch8.PC, 100)
    try:
        ch8.run(steps=200)
    except ValueError as e:
        print(e)

    for i, v in enumerate(ch8.V):
        print(f"V{i:X}={v:02X}", end=" ")
    print(f"I={ch8.I:04X} PC={ch8.PC:04X}")

    ch8.render()

if __name__ == "__main__":
    main()