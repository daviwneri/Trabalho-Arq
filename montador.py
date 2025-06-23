import re
import struct

# funções existentes

def ler_arquivo_asm(caminho):
    with open(caminho, 'r') as arquivo:
        linhas = arquivo.readlines()
    return [linha.strip() for linha in linhas if linha.strip() and not linha.startswith(';')]

def parse_instrucao(linha):
    if ':' in linha:
        label, resto = linha.split(':', 1)
        return {'label': label.strip(), 'instrucao': resto.strip()}
    else:
        return {'label': None, 'instrucao': linha}

def dividir_secoes(linhas):
    secao = None
    data = []
    text = []

    for linha in linhas:
        linha = linha.strip()
        if linha == '.data':
            secao = 'data'
            continue
        elif linha == '.text':
            secao = 'text'
            continue

        if secao == 'data':
            data.append(linha)
        elif secao == 'text':
            text.append(linha)

    return data, text

def expandir_pseudo(instrucao):
    tokens = re.split(r'[,\s]+', instrucao.strip())
    if tokens[0] == 'li':
        return f'addi {tokens[1]}, x0, {tokens[2]}'
    elif tokens[0] == 'mv':
        if tokens[1].startswith('f') or tokens[2].startswith('f'):
            return f'fmv.s {tokens[1]}, {tokens[2]}'
        else:
            return f'addi {tokens[1]}, {tokens[2]}, 0'
    elif tokens[0] == 'j':
        return f'jal x0, {tokens[1]}'
    elif tokens[0] == 'la':
        return f'auipc {tokens[1]}, 0\naddi {tokens[1]}, {tokens[1]}, %lo({tokens[2]})'
    else:
        return instrucao

def primeira_passagem(linhas_texto):
    endereco = 0
    tabela_simbolos = {}
    instrucoes = []

    for linha in linhas_texto:
        parsed = parse_instrucao(linha)
        if parsed['label']:
            tabela_simbolos[parsed['label']] = endereco
        if parsed['instrucao']:
            instrucao_real = expandir_pseudo(parsed['instrucao'])
            instrucoes.append((endereco, instrucao_real))
            endereco += 4

    return tabela_simbolos, instrucoes


def processar_data(data_linhas):
    memoria = bytearray()
    labels = {}
    offset = 0

    for linha in data_linhas:
        try:
            if '.asciz' in linha:
                parts = linha.split(':', 1)
                if len(parts) != 2:
                    continue
                
                label = parts[0].strip()
                conteudo = parts[1].strip()
                
                if '.asciz' in conteudo:
                    string_part = conteudo.split('.asciz')[1].strip()
                    if string_part.count('"') >= 2:
                        string = string_part.split('"')[1]
                        encoded_string = string.encode('utf-8') + b'\x00'
                        labels[label] = offset
                        memoria += encoded_string
                        offset += len(encoded_string)
        except Exception as e:
            print(f"Erro ao processar linha: {linha}\n{str(e)}")
            continue

    return labels, memoria


# montagem das instruções
registradores = {
    f'x{i}': i for i in range(32)
}
registradores.update({
    'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4,
    't0': 5, 't1': 6, 't2': 7, 's0': 8, 'fp': 8, 's1': 9,
    'a0': 10, 'a1': 11, 'a2': 12, 'a3': 13, 'a4': 14, 'a5': 15, 'a6': 16, 'a7': 17,
    's2': 18, 's3': 19, 's4': 20, 's5': 21, 's6': 22, 's7': 23, 's8': 24, 's9': 25, 's10': 26, 's11': 27,
    't3': 28, 't4': 29, 't5': 30, 't6': 31,

    **{f'f{i}': 32+i for i in range(32)},
    **{f'fa{i}': 32+i for i in range(8)}
})

funct3_map = {
    'ADD': 0b000, 'SUB': 0b000, 'MUL': 0b000, 'DIV': 0b100, 'REM': 0b110,
    'XOR': 0b100, 'OR': 0b110, 'AND': 0b111, 'SLL': 0b001, 'SRL': 0b101,
    'ADDI': 0b000, 'LW': 0b010, 'JALR': 0b000,
    'SW': 0b010,
    'BEQ': 0b000, 'BNE': 0b001, 'BGE': 0b101, 'BLT': 0b100,
    'FADD.S': 0b000,
    'FSUB.S': 0b000,
    'FMUL.S': 0b000,
    'FDIV.S': 0b000,
    'FCVT.S.W': 0b111,
    'FMV.S': 0b000
}

funct7_map = {
    'ADD': 0b0000000, 'SUB': 0b0100000, 'MUL': 0b0000001,
    'DIV': 0b0000001, 'REM': 0b0000001, 'XOR': 0b0000000,
    'OR': 0b0000000, 'AND': 0b0000000, 'SLL': 0b0000000,
    'SRL': 0b0000000,
    'FADD.S': 0b0000000,
    'FSUB.S': 0b0000100,
    'FMUL.S': 0b0001000,
    'FDIV.S': 0b0001100,
    'FCVT.S.W': 0b1101000,
    'FMV.S': 0b1111000
}

opcode_map = {
    'R': 0b0110011,
    'I': 0b0010011,
    'LW': 0b0000011,
    'SW': 0b0100011,
    'B': 0b1100011,
    'JAL': 0b1101111,
    'JALR': 0b1100111
}

def montar_instrucao(instrucao, labels, pc):
    if '\n' in instrucao:
        partes = instrucao.split('\n')
        codigo_binario = bytearray()
        for parte in partes:
            if parte.strip():
                codigo_binario += montar_instrucao(parte, labels, pc)
                pc += 4
        return codigo_binario

    instrucao = ' '.join(instrucao.split())
    tokens = re.split(r'[,\s]+', instrucao.strip())
    if not tokens:
        return b'\x00\x00\x00\x00'

    instr = tokens[0].upper()
    
    def reg(nome):
        return registradores.get(nome.lower(), 0)
    
    def imm(valor):
        if isinstance(valor, int):
            return valor
        if valor in labels:
            return labels[valor]
        try:
            return int(valor, 0)
        except ValueError:
            return 0

    if instr in ['ADD', 'SUB', 'MUL', 'DIV', 'REM', 'XOR', 'OR', 'AND', 'SLL', 'SRL']:
        rd, rs1, rs2 = reg(tokens[1]), reg(tokens[2]), reg(tokens[3])
        funct3 = funct3_map[instr]
        funct7 = funct7_map.get(instr, 0)
        opcode = opcode_map['R']
        return struct.pack('<I', (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | 
                          (funct3 << 12) | (rd << 7) | opcode)

    elif instr in ['ADDI', 'ANDI', 'ORI', 'XORI']:
        rd, rs1, imm12 = reg(tokens[1]), reg(tokens[2]), imm(tokens[3]) & 0xFFF
        funct3 = funct3_map[instr]
        opcode = opcode_map['I']
        return struct.pack('<I', (imm12 << 20) | (rs1 << 15) | 
                          (funct3 << 12) | (rd << 7) | opcode)

    elif instr == 'LW':
        rd = reg(tokens[1])
        offset_rs1 = tokens[2]
        offset, base = re.match(r'(\d+)\((\w+)\)', offset_rs1).groups()
        funct3 = funct3_map['LW']
        opcode = opcode_map['LW']
        return struct.pack('<I', (int(offset) << 20) | (reg(base) << 15) | 
                          (funct3 << 12) | (rd << 7) | opcode)

    elif instr == 'SW':
        rs2 = reg(tokens[1])
        offset_rs1 = tokens[2]
        offset, base = re.match(r'(\d+)\((\w+)\)', offset_rs1).groups()
        offset = int(offset)
        imm11_5 = (offset >> 5) & 0x7F
        imm4_0 = offset & 0x1F
        funct3 = funct3_map['SW']
        opcode = opcode_map['SW']
        return struct.pack('<I', (imm11_5 << 25) | (rs2 << 20) | (reg(base) << 15) | 
                          (funct3 << 12) | (imm4_0 << 7) | opcode)

    elif instr in ['BEQ', 'BNE', 'BLT', 'BGE']:
        rs1, rs2 = reg(tokens[1]), reg(tokens[2])
        label = tokens[3]
        offset = (labels[label] - pc) & 0x1FFF
        funct3 = funct3_map[instr]
        opcode = opcode_map['B']
        
        imm12 = (offset >> 12) & 0x1
        imm10_5 = (offset >> 5) & 0x3F
        imm4_1 = (offset >> 1) & 0xF
        imm11 = (offset >> 11) & 0x1
        
        return struct.pack('<I', (imm12 << 31) | (imm10_5 << 25) | (rs2 << 20) | 
                          (rs1 << 15) | (funct3 << 12) | (imm4_1 << 8) | 
                          (imm11 << 7) | opcode)
    

    elif instr == 'JAL':
        rd = reg(tokens[1])
        label = tokens[2]
        offset = (labels[label] - pc) & 0x1FFFFF
        opcode = opcode_map['JAL']
        
        imm20 = (offset >> 20) & 0x1
        imm10_1 = (offset >> 1) & 0x3FF
        imm11 = (offset >> 11) & 0x1
        imm19_12 = (offset >> 12) & 0xFF
        
        return struct.pack('<I', (imm20 << 31) | (imm19_12 << 12) | (imm11 << 20) | 
                          (imm10_1 << 21) | (rd << 7) | opcode)

    elif instr == 'JALR':
        rd, rs1 = reg(tokens[1]), reg(tokens[2])
        imm12 = imm(tokens[3]) & 0xFFF
        funct3 = funct3_map['JALR']
        opcode = opcode_map['JALR']
        return struct.pack('<I', (imm12 << 20) | (rs1 << 15) | 
                          (funct3 << 12) | (rd << 7) | opcode)
    
    elif instr in ['FADD.S', 'FSUB.S', 'FMUL.S', 'FDIV.S']:
        rd = reg(tokens[1])
        rs1 = reg(tokens[2])
        rs2 = reg(tokens[3])
        funct3 = funct3_map[instr]
        funct7 = funct7_map[instr]
        opcode = 0b1010011  # OP-FP
        return struct.pack('<I', (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | 
                          (funct3 << 12) | (rd << 7) | opcode)

    elif instr == 'FCVT.S.W':
        rd = reg(tokens[1])
        rs1 = reg(tokens[2])
        funct3 = funct3_map[instr]
        funct7 = funct7_map[instr]
        opcode = 0b1010011  # OP-FP
        return struct.pack('<I', (funct7 << 25) | (0b00000 << 20) | (rs1 << 15) | 
                          (funct3 << 12) | (rd << 7) | opcode)

    elif instr == 'FMV.S':
        rd = reg(tokens[1])
        rs1 = reg(tokens[2])
        funct3 = funct3_map[instr]
        funct7 = funct7_map[instr]
        opcode = 0b1010011  # OP-FP
        return struct.pack('<I', (funct7 << 25) | (0b00000 << 20) | (rs1 << 15) | 
                          (funct3 << 12) | (rd << 7) | opcode)

    elif instr == 'AUIPC':
        rd = reg(tokens[1])
        imm20 = (imm(tokens[2]) >> 12) & 0xFFFFF
        opcode = 0b0010111
        return struct.pack('<I', (imm20 << 12) | (rd << 7) | opcode)

    elif instr == 'NOP':
        return struct.pack('<I', 0x00000013)
    
    elif instr == 'ECALL':
        return struct.pack('<I', 0x00000073)
    
    elif instr == 'EBREAK':
        return struct.pack('<I', 0x00100073)

    else:
        raise ValueError(f'Instrução não suportada: {instrucao}')
    
    
# main
def main(caminho_entrada, caminho_saida=None):
    linhas = ler_arquivo_asm(caminho_entrada)
    data_linhas, text_linhas = dividir_secoes(linhas)

    if caminho_saida is None:
        caminho_saida = caminho_entrada.rsplit('.', 1)[0] + '.bin'

    labels_data, memoria_data = processar_data(data_linhas)
    labels_text, instrucoes = primeira_passagem(text_linhas)
    labels = {**labels_data, **labels_text}

    memoria_text = bytearray()
    for endereco, instrucao in instrucoes:
        bytes_instrucao = montar_instrucao(instrucao, labels, endereco)
        memoria_text += bytes_instrucao

    with open(caminho_saida, 'wb') as f:
        f.write(memoria_data)
        f.write(memoria_text)


# chamada da main
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Uso: python montador.py entrada.asm [saida.bin]")
        print("Se saida.bin não for fornecido, será gerado automaticamente")
    else:
        entrada = sys.argv[1]
        saida = sys.argv[2] if len(sys.argv) > 2 else None
        main(entrada, saida)
