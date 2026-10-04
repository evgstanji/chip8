from typing import NamedTuple

PROGRAM_START = 0x200
BYTES_PER_LINE = 16
OPCODE_SIZE = 2

# display resolution
HEIGHT = 32
WIDTH = 64

class Instruction(NamedTuple):
    kind: int
    x: int
    y: int
    n: int
    nn: int
    nnn: int

class Chip8:
    def __init__(self) -> None:
        self.display = bytearray(WIDTH * HEIGHT)
        self.memory = bytearray(4096)
        self.PC = PROGRAM_START
        self.V = [0x0] * 16
        self.I = 0x0
        
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
            case 0x1:
                self.PC = ins.nnn
            case 0x6:
                self.V[ins.x] = ins.nn
            case 0x7:
                self.V[ins.x] = (ins.nn + self.V[ins.x]) & 0xFF  
            case 0xA:
                self.I = ins.nnn
            case 0xD:
                x0 = self.V[ins.x] % WIDTH      
                y0 = self.V[ins.y] % HEIGHT
                for row in range(ins.n):
                    sprite_byte = self.memory[self.I + row]           
                    for col in range(8):
                        bit = (sprite_byte >> (7 - col)) & 1               
                        x = x0 + col
                        y = y0 + row
                        if x >= WIDTH or y >= HEIGHT:
                            continue            
                        self.display[y * WIDTH + x] ^= bit
            case _:
                opcode = (ins.kind << 12) | ins.nnn
                raise ValueError(f"Unknown opcode: {opcode:04X}")
        
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
    ch8.load_rom("./logo.ch8")
    ch8.dump(ch8.PC, 100)
    try:
        ch8.run(steps=100)
    except ValueError as e:
        print(e)
        
    for i, v in enumerate(ch8.V):
        print(f"V{i:X}={v:02X}", end=" ")
    print(f"I={ch8.I:04X} PC={ch8.PC:04X}")
    
    ch8.render()
    
if __name__ == "__main__":
    main()