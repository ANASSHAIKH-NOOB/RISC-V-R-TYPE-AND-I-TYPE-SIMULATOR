from cpu_state import CPUState


def sign_extend_32(value):
    value = value & 0xFFFFFFFF
    if value >= 0x80000000:
        value -= 0x100000000
    return value


def execute(instructions):
    cpu = CPUState()
    log = []

    for instr in instructions:
        binary = instr['binary']
        source = instr['source']

        opcode = binary & 0x7F
        rd = (binary >> 7) & 0x1F
        funct3 = (binary >> 12) & 0x7
        rs1 = (binary >> 15) & 0x1F
        rs2 = (binary >> 20) & 0x1F
        funct7 = (binary >> 25) & 0x7F

        imm_raw = (binary >> 20) & 0xFFF
        imm = imm_raw if imm_raw < 0x800 else imm_raw - 0x1000

        v1 = cpu.read_reg(rs1)
        v2 = cpu.read_reg(rs2)

        sv1 = sign_extend_32(v1)
        sv2 = sign_extend_32(v2)

        result = None

        if opcode == 0b0110011:
            if funct3 == 0b000 and funct7 == 0b0000000:
                result = v1 + v2
            elif funct3 == 0b000 and funct7 == 0b0100000:
                result = v1 - v2
            elif funct3 == 0b111:
                result = v1 & v2
            elif funct3 == 0b110:
                result = v1 | v2
            elif funct3 == 0b100:
                result = v1 ^ v2
            elif funct3 == 0b001:
                result = v1 << (v2 & 0x1F)
            elif funct3 == 0b101 and funct7 == 0b0000000:
                result = v1 >> (v2 & 0x1F)
            elif funct3 == 0b101 and funct7 == 0b0100000:
                result = sv1 >> (v2 & 0x1F)
            elif funct3 == 0b010:
                result = 1 if sv1 < sv2 else 0
            elif funct3 == 0b011:
                result = 1 if v1 < v2 else 0
            else:
                raise ValueError(f"Unknown R-type funct3={funct3} funct7={funct7}: '{source}'")

            cpu.write_reg(rd, result)

        elif opcode == 0b0010011:
            shamt = imm & 0x1F

            if funct3 == 0b000:
                result = v1 + imm
            elif funct3 == 0b111:
                result = v1 & imm
            elif funct3 == 0b110:
                result = v1 | imm
            elif funct3 == 0b100:
                result = v1 ^ imm
            elif funct3 == 0b010:
                result = 1 if sv1 < imm else 0
            elif funct3 == 0b011:
                result = 1 if v1 < (imm & 0xFFF) else 0
            elif funct3 == 0b001:
                result = v1 << shamt
            elif funct3 == 0b101 and funct7 == 0b0000000:
                result = v1 >> shamt
            elif funct3 == 0b101 and funct7 == 0b0100000:
                result = sv1 >> shamt
            else:
                raise ValueError(f"Unknown I-arith funct3={funct3}: '{source}'")

            cpu.write_reg(rd, result)

        elif opcode == 0b0000011 and funct3 == 0b010:
            addr = (v1 + imm) & 0xFFFFFFFF
            result = cpu.read_mem(addr)
            cpu.write_reg(rd, result)

        elif opcode == 0b1100111 and funct3 == 0b000:
            return_addr = cpu.pc + 4
            cpu.write_reg(rd, return_addr)
            cpu.pc = (v1 + imm) & 0xFFFFFFFE
            result = return_addr

        else:
            raise ValueError(f"Unknown opcode {bin(opcode)}: '{source}'")

        log.append({
            'pc': instr['address'],
            'source': source,
            'rd': f"x{rd}",
            'result': result & 0xFFFFFFFF if result is not None else None,
        })

        if opcode != 0b1100111:
            cpu.pc += 4

    return {'registers': cpu.registers, 'memory': cpu.memory, 'log': log}

