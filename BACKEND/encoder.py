import isa_tables

def encode_r(name, rd, rs1, rs2):
    opcode = OPCODES[name]
    funct3 = FUNCT3[name]
    funct7 = FUNCT7.get[name, 0b0000000]  # Default to 0 for I-type instructions
    instruction = (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
    return instruction

def encode_i(name, rd, rs1, imm):
    opcode = OPCODES[name]
    funct3 = FUNCT3[name]
    instruction = (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
    return instruction

