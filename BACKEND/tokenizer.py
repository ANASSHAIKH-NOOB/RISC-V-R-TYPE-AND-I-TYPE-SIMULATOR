import re

ABI_NAMES = {
    'zero': 'x0',  'ra': 'x1',  'sp': 'x2',  'gp': 'x3',
    'tp': 'x4',    't0': 'x5',  't1': 'x6',  't2': 'x7',
    's0': 'x8',    's1': 'x9',
    'a0': 'x10',   'a1': 'x11', 'a2': 'x12', 'a3': 'x13',
    'a4': 'x14',   'a5': 'x15', 'a6': 'x16', 'a7': 'x17',
    's2': 'x18',   's3': 'x19', 's4': 'x20', 's5': 'x21',
    's6': 'x22',   's7': 'x23', 's8': 'x24', 's9': 'x25',
    's10': 'x26',  's11': 'x27',
    't3': 'x28',   't4': 'x29', 't5': 'x30', 't6': 'x31'
}


def parse_operand(op):
    op = op.strip()
    if op in ABI_NAMES:                              # catch any missed ABI names
        op = ABI_NAMES[op]
    if op.startswith('0x') or op.startswith('0X'):
        return int(op, 16)
    if op.startswith('x') and op[1:].isdigit():     # it's already xN
        return int(op[1:])                           # return the register number
    if op.lstrip('-').isdigit():                     # immediate (positive or negative)
        return int(op)
    return op      
    

def tokenize(source_code):
    token_list = []
    for line in source_code.split('\n'):
        line = line.strip()
        if '#' in line:
            line = line.split('#')[0].strip()
        if not line:
            continue
        if line.endswith(':'):
            label_name = line[:-1].strip()
            token_list.append({
                'type': 'LABEL', 
                'value': label_name
            })
            continue
        
        parts = line.split(None, 1)
        mnemonic_raw = parts[0]
        operand_str = parts[1] if len(parts) > 1 else ''

        operand_str = re.sub(
            r'\b(zero|ra|sp|gp|tp|t[0-6]|s[0-9]+|a[0-7]|x\d+)\b',
            lambda m: ABI_NAMES.get(m.group(1), m.group(1)),
            operand_str
        )

        line = mnemonic_raw + ' ' + operand_str

        line = re.sub(r'(-?\d+)\(([^)]+)\)', r'\1, \2', line)

        raw_parts = re.split(r'[\s,]+', line)
        raw_parts = [part for part in raw_parts if part]

        if not raw_parts:
            continue
        
        mnemonic = raw_parts[0].upper()
        
        operands = [parse_operand(op) for op in raw_parts[1:]]
        token_list.append({
            'type': 'INSTRUCTION',
            'mnemonic': mnemonic,
            'operands': operands
        })

    return token_list