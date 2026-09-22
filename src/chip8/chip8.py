PROGRAM_START = 0x200
BYTES_PER_LINE = 16
OPCODE_SIZE = 2

class Chip8:
    def __init__(self) -> None:
        self.memory = bytearray(4096)
        self.PC = PROGRAM_START
        self.V = [0x0] * 16
        self.I = 0x0
        
    def load_rom(self, path) -> None:
        with open(path, 'rb') as file:
            data = file.read()
        self.memory[PROGRAM_START: PROGRAM_START + len(data)] = data
    
    def dump(self, start, count) -> None:
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
    
    def decode(self, opcode):
        # вернуть (kind, x, y, n, nn, nnn)
        ...
        
        
    
def main() -> None:
    ch8 = Chip8()
    ch8.load_rom("./logo.ch8")
    ch8.dump(0x200, 15)
    
    for _ in range(10):
        addr = ch8.PC
        op = ch8.fetch()
        print(f"{addr:04X}: {op:04X}")
    

if __name__ == "__main__":
    main()