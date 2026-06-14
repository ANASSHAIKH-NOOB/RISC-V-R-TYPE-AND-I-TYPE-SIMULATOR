# assembler.py
from tokenizer import tokenize
from encoder import encode_r, encode_i

# These are the sets used to decide which encoder to call
R_TYPES = {'ADD', 'SUB', 'AND', 'OR', 'XOR', 'SLL', 'SRL', 'SRA', 'SLT', 'SLTU'}
I_TYPES = {'ADDI', 'ANDI', 'ORI', 'XORI', 'SLTI', 'SLTIU', 'SLLI', 'SRLI', 'SRAI', 'LW', 'JALR'}

def assemble(source_code):
    """
    Takes raw assembly string, returns a list of dicts:
    [{ 'address': int, 'binary': int, 'source': str }, ...]
    """
    tokens = tokenize(source_code)      # Step 1: get clean token list
    instructions = []
    pc = 0                              # Program counter, starts at 0, +4 per instruction

    for token in tokens:

        # Skip label tokens — we don't encode them
        if token['type'] == 'label':
            continue

        mnemonic = token['mnemonic']
        operands = token['operands']    # already parsed ints/strings from tokenizer
        source   = f"{mnemonic} {', '.join(str(o) for o in operands)}"

        # ── R-TYPE ──────────────────────────────────────────────
        # Syntax: ADD rd, rs1, rs2
        # operands = [rd(int), rs1(int), rs2(int)]
        if mnemonic in R_TYPES:
            if len(operands) != 3:
                raise ValueError(f"Line '{source}': R-type expects 3 operands, got {len(operands)}")

            rd, rs1, rs2 = operands[0], operands[1], operands[2]
            binary = encode_r(mnemonic, rd, rs1, rs2)

        # ── I-TYPE (normal) ─────────────────────────────────────
        # Syntax: ADDI rd, rs1, imm
        # operands = [rd(int), rs1(int), imm(int)]
        elif mnemonic in I_TYPES and mnemonic != 'LW':
            if len(operands) != 3:
                raise ValueError(f"Line '{source}': I-type expects 3 operands, got {len(operands)}")

            rd, rs1, imm = operands[0], operands[1], operands[2]

            # Immediate must be a plain int
            if not isinstance(imm, int):
                raise ValueError(f"Line '{source}': expected immediate, got '{imm}'")

            # Immediate range check: I-type imm is 12-bit signed → [-2048, 2047]
            if not (-2048 <= imm <= 2047):
                raise ValueError(f"Line '{source}': immediate {imm} out of 12-bit range [-2048, 2047]")

            binary = encode_i(mnemonic, rd, rs1, imm)

        # ── I-TYPE (LW special case) ─────────────────────────────
        # Syntax: LW rd, offset(rs1)  →  tokenizer expands to [rd, offset, rs1]
        # operands = [rd(int), offset(int), rs1(int)]
        elif mnemonic == 'LW':
            if len(operands) != 3:
                raise ValueError(f"Line '{source}': LW expects rd, offset(rs1) format")

            rd     = operands[0]
            offset = operands[1]    # this is the immediate
            rs1    = operands[2]
            binary = encode_i('LW', rd, rs1, offset)

        else:
            raise ValueError(f"Unknown instruction: '{mnemonic}'")

        # Append encoded instruction with its address and original source text
        instructions.append({
            'address': pc,
            'binary':  binary,
            'source':  source
        })

        pc += 4     # Each instruction is 4 bytes (32-bit)

    return instructions 