class CPUState:
    def __init__(self):
        self.registers = [0] * 32
        self.pc = 0
        self.memory = {}

    def write_reg(self, rd, value):
        if 0 <= rd < len(self.registers):
            self.registers[rd] = value & 0xFFFFFFFF
        else:
            raise ValueError("Invalid register number")

    def read_reg(self, rs):
        if 0 <= rs < len(self.registers):
            return self.registers[rs]
        else:
            raise ValueError("Invalid register number")

    def read_memory(self, address):
        return self.memory.get(address, 0)

    def write_memory(self, address, value):
        self.memory[address] = value & 0xFFFFFFFF

