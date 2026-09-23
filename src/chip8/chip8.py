from typing import NamedTuple

PROGRAM_START = 0x200
BYTES_PER_LINE = 16
OPCODE_SIZE = 2

class Instruction(NamedTuple):
    kind: int
    x: int
    y: int
    n: int
    nn: int
    nnn: int

class Chip8:
    def __init__(self) -> None:
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
        
    
def main() -> None:
    ch8 = Chip8()
    ch8.load_rom("./logo.ch8")
    ch8.dump(0x200, 15)
        
    for _ in range(10):
        addr = ch8.PC
        opcode = ch8.fetch()
        ins = ch8.decode(opcode)
        print(f"{addr:04X}: {opcode:04X}  kind={ins.kind:X} X={ins.x:X} Y={ins.y:X} N={ins.n:X} NN={ins.nn:02X} NNN={ins.nnn:03X}")
    

if __name__ == "__main__":
    main()