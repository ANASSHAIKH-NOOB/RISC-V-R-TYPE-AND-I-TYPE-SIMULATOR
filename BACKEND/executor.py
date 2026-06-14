# executor.py
from cpu_state import CPUState

def sign_extend_32(value):
    """
    Python ints don't overflow. After arithmetic we mask to 32 bits,
    then convert to signed so comparisons (SLT, SLTI) work correctly.
    """
    value = value & 0xFFFFFFFF          # keep only lower 32 bits
    if value >= 0x80000000:             # if bit 31 is set, it's negative
        value -= 0x100000000            # convert to negative Python int
    return value

def execute(instructions):
    """
    Runs the list of encoded instructions produced by assembler.py.
    Returns { 'registers': list[32], 'memory': dict, 'log': list }
    """
    cpu = CPUState()
    log = []

    for instr in instructions:
        binary = instr['binary']
        source = instr['source']

        # ── Decode every field from the 32-bit word ──────────────
        opcode = binary & 0x7F                  # bits  [6:0]
        rd     = (binary >> 7)  & 0x1F          # bits [11:7]
        funct3 = (binary >> 12) & 0x7           # bits [14:12]
        rs1    = (binary >> 15) & 0x1F          # bits [19:15]
        rs2    = (binary >> 20) & 0x1F          # bits [24:20]  — R-type only
        funct7 = (binary >> 25) & 0x7F          # bits [31:25]  — R-type only

        # I-type immediate: bits [31:20], needs sign extension
        imm_raw = (binary >> 20) & 0xFFF        # 12 unsigned bits
        imm = imm_raw if imm_raw < 0x800 else imm_raw - 0x1000   # sign extend

        # Read register values (unsigned 32-bit stored in cpu)
        v1 = cpu.read_reg(rs1)
        v2 = cpu.read_reg(rs2)

        # Signed versions for comparison instructions
        sv1 = sign_extend_32(v1)
        sv2 = sign_extend_32(v2)

        result = None       # will be set by each branch below

        # ── R-TYPE: opcode = 0110011 ─────────────────────────────
        if opcode == 0b0110011:

            if   funct3 == 0b000 and funct7 == 0b0000000:  result = v1 + v2            # ADD
            elif funct3 == 0b000 and funct7 == 0b0100000:  result = v1 - v2            # SUB
            elif funct3 == 0b111:                           result = v1 & v2            # AND
            elif funct3 == 0b110:                           result = v1 | v2            # OR
            elif funct3 == 0b100:                           result = v1 ^ v2            # XOR
            elif funct3 == 0b001:                           result = v1 << (v2 & 0x1F) # SLL
            elif funct3 == 0b101 and funct7 == 0b0000000:  result = v1 >> (v2 & 0x1F) # SRL (logical)
            elif funct3 == 0b101 and funct7 == 0b0100000:  result = sv1 >> (v2 & 0x1F)# SRA (arithmetic)
            elif funct3 == 0b010:                           result = 1 if sv1 < sv2 else 0  # SLT
            elif funct3 == 0b011:                           result = 1 if v1  < v2  else 0  # SLTU
            else:
                raise ValueError(f"Unknown R-type funct3={funct3} funct7={funct7}: '{source}'")

            cpu.write_reg(rd, result)

        # ── I-TYPE ARITHMETIC: opcode = 0010011 ──────────────────
        elif opcode == 0b0010011:

            shamt = imm & 0x1F      # shift amount: only lower 5 bits used

            if   funct3 == 0b000:                           result = v1 + imm           # ADDI
            elif funct3 == 0b111:                           result = v1 & imm           # ANDI
            elif funct3 == 0b110:                           result = v1 | imm           # ORI
            elif funct3 == 0b100:                           result = v1 ^ imm           # XORI
            elif funct3 == 0b010:                           result = 1 if sv1 < imm  else 0  # SLTI
            elif funct3 == 0b011:                           result = 1 if v1  < (imm & 0xFFF) else 0  # SLTIU
            elif funct3 == 0b001:                           result = v1 << shamt        # SLLI
            elif funct3 == 0b101 and funct7 == 0b0000000:  result = v1 >> shamt        # SRLI
            elif funct3 == 0b101 and funct7 == 0b0100000:  result = sv1 >> shamt       # SRAI
            else:
                raise ValueError(f"Unknown I-arith funct3={funct3}: '{source}'")

            cpu.write_reg(rd, result)

        # ── LW: opcode = 0000011 ─────────────────────────────────
        # Load word: rd = Memory[rs1 + imm]
        elif opcode == 0b0000011 and funct3 == 0b010:
            addr = (v1 + imm) & 0xFFFFFFFF
            result = cpu.read_mem(addr)
            cpu.write_reg(rd, result)

        # ── JALR: opcode = 1100111 ───────────────────────────────
        # rd = PC + 4,  PC = (rs1 + imm) & ~1
        elif opcode == 0b1100111 and funct3 == 0b000:
            return_addr = cpu.pc + 4
            cpu.write_reg(rd, return_addr)
            cpu.pc = (v1 + imm) & 0xFFFFFFFE   # clear lowest bit (spec requirement)
            result = return_addr

        else:
            raise ValueError(f"Unknown opcode {bin(opcode)}: '{source}'")

        # ── Log this instruction ──────────────────────────────────
        log.append({
            'pc':     instr['address'],
            'source': source,
            'rd':     f"x{rd}",
            'result': result & 0xFFFFFFFF if result is not None else None
        })

        # Only advance PC normally if JALR didn't already change it
        if opcode != 0b1100111:
            cpu.pc += 4

    return {
        'registers': cpu.registers,
        'memory':    cpu.memory,
        'log':       log
    }