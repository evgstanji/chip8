PROGRAM_START = 0x200

class Chip8:
    def __init__(self):
        self.memory = bytearray(4096)
        self.PS = PROGRAM_START
        self.V = [0x0] * 16
        self.I = 0x0
        
    def load_rom(self, path):
        with open(path, 'rb') as file:
            data = file.read()
   
        self.memory[PROGRAM_START: PROGRAM_START + len(data)] = data
    
    def dump(self, start, count):
        LENGHT_LINE = 16
        for addr in range(start, start + count, LENGHT_LINE):
            row = self.memory[addr : addr + LENGHT_LINE]
            hex_line = " ".join(f"{byte:02X}" for byte in row)
            
            print(f"{addr:04X}: {hex_line}")
    
def main():
    ch8 = Chip8()
    ch8.load_rom("./logo.ch8")
    ch8.dump(0x200, 100)

if __name__ == "__main__":
    main()