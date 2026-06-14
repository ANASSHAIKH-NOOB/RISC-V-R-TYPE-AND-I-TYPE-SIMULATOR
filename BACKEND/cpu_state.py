class CPUState:
    def __init__(self):
        self.registers = [0] * 32  # 32 general-purpose registers
        self.pc = 0  # Program counter
        self.memory = {}  # Simulated memory as a dictionary
    
    def write_reg(self, rd, value):
        if 0 <= rd < len(self.registers):
            self.registers[rd] = value & 0xFFFFFFFF  # Ensure 32-bit value
        else:
            raise ValueError("Invalid register number")
    
    def read_reg(self, rs):
        if 0 <= rs < len(self.registers):
            return self.registers[rs]
        else:
            raise ValueError("Invalid register number")
        
    def read_memory(self, address):
        return self.memory.get(address, 0)  # Return 0 if address is not set
    
    def write_memory(self, address, value):
        self.memory[address] = value & 0xFFFFFFFF  # Ensure 32-bit value

    