from tokenizer import tokenize
from encoder import encode_r, encode_i

R_TYPES = {'ADD', 'SUB', 'AND', 'OR', 'XOR', 'SLL', 'SRL', 'SRA', 'SLT', 'SLTU'}
I_TYPES = {'ADDI', 'ANDI', 'ORI', 'XORI', 'SLTI', 'SLTIU', 'SLLI', 'SRLI', 'SRAI', 'LW', 'JALR'}

def assemble(source_code):
    tokens = tokenize(source_code)
    instructions = []
    pc = 0

    for token in tokens:
        if token['type'] == 'label':
            continue

        mnemonic = token['mnemonic']
        operands = token['operands']
        source = f"{mnemonic} {', '.join(str(o) for o in operands)}"

        if mnemonic in R_TYPES:
            if len(operands) != 3:
                raise ValueError(f"Line '{source}': R-type expects 3 operands, got {len(operands)}")

            rd, rs1, rs2 = operands[0], operands[1], operands[2]
            binary = encode_r(mnemonic, rd, rs1, rs2)

        elif mnemonic in I_TYPES and mnemonic != 'LW':
            if len(operands) != 3:
                raise ValueError(f"Line '{source}': I-type expects 3 operands, got {len(operands)}")

            rd, rs1, imm = operands[0], operands[1], operands[2]

            if not isinstance(imm, int):
                raise ValueError(f"Line '{source}': expected immediate, got '{imm}'")

            if not (-2048 <= imm <= 2047):
                raise ValueError(f"Line '{source}': immediate {imm} out of 12-bit range [-2048, 2047]")

            binary = encode_i(mnemonic, rd, rs1, imm)

        elif mnemonic == 'LW':
            if len(operands) != 3:
                raise ValueError(f"Line '{source}': LW expects rd, offset(rs1) format")

            rd = operands[0]
            offset = operands[1]
            rs1 = operands[2]
            binary = encode_i('LW', rd, rs1, offset)

        else:
            raise ValueError(f"Unknown instruction: '{mnemonic}'")

        instructions.append({'address': pc, 'binary': binary, 'source': source})
        pc += 4

    return instructions

