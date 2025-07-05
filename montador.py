import re
import struct

class Montador:
    def __init__(self):
        self.registradores = self._init_registers()
        self.funct3_map = self._init_funct3()
        self.funct7_map = self._init_funct7()
        self.opcode_map = self._init_opcodes()
        
    def _init_registers(self):
        """Inicializa o mapeamento de registradores"""
        registradores = {f'x{i}': i for i in range(32)}
        registradores.update({
            'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4,
            't0': 5, 't1': 6, 't2': 7, 's0': 8, 'fp': 8, 's1': 9,
            'a0': 10, 'a1': 11, 'a2': 12, 'a3': 13, 'a4': 14, 'a5': 15,
            'a6': 16, 'a7': 17
        })
        return registradores

    def _init_funct3(self):
        """Mapeamento de funct3 para instruções"""
        return {
            'ADD': 0b000, 'SUB': 0b000, 'MUL': 0b000, 'DIV': 0b100, 'REM': 0b110,
            'XOR': 0b100, 'AND': 0b111, 'OR': 0b110, 'SLL': 0b001, 'SRL': 0b101,
            'SLLI': 0b001, 'SRLI': 0b101,
            'ADDI': 0b000, 'LW': 0b010, 'JALR': 0b000,
            'SW': 0b010, 'BEQ': 0b000, 'BNE': 0b001, 'BGE': 0b101, 'BLT': 0b100
        }

    def _init_funct7(self):
        """Mapeamento de funct7 para instruções"""
        return {
            'ADD': 0b0000000, 'SUB': 0b0100000, 'MUL': 0b0000001,
            'DIV': 0b0000001, 'REM': 0b0000001, 'XOR': 0b0000000,
            'AND': 0b0000000, 'OR': 0b0000000, 'SLL': 0b0000000,
            'SRL': 0b0000000, 'SLLI': 0b0000000, 'SRLI': 0b0000000
        }

    def _init_opcodes(self):
        """Mapeamento de opcodes para formatos de instrução"""
        return {
            'R': 0b0110011, 'I': 0b0010011, 'S': 0b0100011,
            'B': 0b1100011, 'J': 0b1101111, 'LW': 0b0000011,
            'JALR': 0b1100111
        }

    def ler_arquivo(self, caminho):
        """Lê o arquivo de entrada e remove comentários e linhas vazias"""
        with open(caminho, 'r', encoding='utf-8') as f:
            return [linha.split('#')[0].strip() 
                    for linha in f 
                    if linha.strip() and not linha.startswith('#')]

    def dividir_secoes(self, linhas):
        """Divide o código nas seções .data e .text"""
        secao = None
        data = []
        text = []
        
        for linha in linhas:
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

    def parse_instrucao(self, linha):
        """Extrai labels e instruções de uma linha"""
        if ':' in linha:
            label, resto = linha.split(':', 1)
            return {'label': label.strip(), 'instrucao': resto.strip()}
        return {'label': None, 'instrucao': linha.strip()}

    def processar_data(self, linhas_data):
        """Processa a seção .data"""
        labels = {}
        memoria = bytearray()
        offset = 0
        
        for linha in linhas_data:
            try:
                if '.word' in linha:
                    label, valores = linha.split(':', 1)
                    label = label.strip()
                    valores = [int(v.strip()) for v in valores.split('.word')[1].split(',')]
                    labels[label] = offset
                    for valor in valores:
                        memoria += struct.pack('<i', valor)
                    offset += len(valores) * 4
            except Exception as e:
                raise ValueError(f"Erro processando .data: {linha}\n{str(e)}")
                
        return labels, memoria

    def primeira_passagem(self, linhas_text):
        """Primeira passagem para construir tabela de símbolos"""
        labels = {}
        instrucoes = []
        pc = 0
        
        for linha in linhas_text:
            parsed = self.parse_instrucao(linha)
            
            if parsed['label']:
                labels[parsed['label']] = pc
                
            if parsed['instrucao']:
                instrucoes.append((pc, parsed['instrucao']))
                pc += 4
                    
        return labels, instrucoes

    def montar_instrucao(self, instrucao, labels, pc):
        """Monta uma única instrução em código de máquina"""
        tokens = re.split(r'[,\s]+', instrucao.strip())
        tokens = [t for t in tokens if t]
        if not tokens:
            return b'\x00\x00\x00\x00'

        instr = tokens[0].upper()
        
        def reg(nome):
            return self.registradores.get(nome.lower(), 0)
            
        def imm(valor):
            if valor in labels:
                return labels[valor]
            try:
                return int(valor, 0)
            except ValueError:
                raise ValueError(f"Valor imediato inválido: {valor}")

        # Tipo R: ADD, SUB, MUL, DIV, REM, XOR, AND, OR, SLL, SRL
        if instr in ['ADD', 'SUB', 'MUL', 'DIV', 'REM', 'XOR', 'AND', 'OR', 'SLL', 'SRL']:
            if len(tokens) != 4:
                raise ValueError(f"Formato inválido para {instr}: esperado RD, RS1, RS2")
            
            rd, rs1, rs2 = reg(tokens[1]), reg(tokens[2]), reg(tokens[3])
            funct3 = self.funct3_map[instr]
            funct7 = self.funct7_map[instr]
            opcode = self.opcode_map['R']
            
            return struct.pack('<I', (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | 
                             (funct3 << 12) | (rd << 7) | opcode)

        # Tipo I: ADDI, SLLI, SRLI, LW, JALR
        elif instr in ['ADDI', 'SLLI', 'SRLI', 'LW', 'JALR']:
            if instr == 'LW':
                if len(tokens) != 3:
                    raise ValueError("Formato inválido para LW: esperado RD, offset(RS1)")
                
                rd = reg(tokens[1])
                
                # Extrai offset e base
                try:
                    offset, base = re.match(r'(\d+)\((\w+)\)', tokens[2]).groups()
                    imm12 = int(offset) & 0xFFF
                    rs1 = reg(base)
                except:
                    raise ValueError(f"Formato inválido para LW: {tokens[2]}")
                
                funct3 = self.funct3_map['LW']
                opcode = self.opcode_map['LW']
            else:
                if len(tokens) != 4:
                    raise ValueError(f"Formato inválido para {instr}: esperado RD, RS1, IMM")
                
                rd = reg(tokens[1])
                rs1 = reg(tokens[2])
                
                if instr in ['SLLI', 'SRLI']:
                    imm12 = imm(tokens[3]) & 0x1F  # Apenas 5 bits para shifts
                else:
                    imm12 = imm(tokens[3]) & 0xFFF  # 12 bits para outras instruções
                
                funct3 = self.funct3_map[instr]
                opcode = self.opcode_map['I'] if instr != 'JALR' else self.opcode_map['JALR']
            
            return struct.pack('<I', (imm12 << 20) | (rs1 << 15) | 
                             (funct3 << 12) | (rd << 7) | opcode)

        # Tipo S: SW
        elif instr == 'SW':
            if len(tokens) != 3:
                raise ValueError("Formato inválido para SW: esperado RS2, offset(RS1)")
            
            rs2 = reg(tokens[1])
            offset, rs1 = re.match(r'(\d+)\((\w+)\)', tokens[2]).groups()
            offset = int(offset)
            
            imm11_5 = (offset >> 5) & 0x7F
            imm4_0 = offset & 0x1F
            funct3 = self.funct3_map['SW']
            opcode = self.opcode_map['S']
            
            return struct.pack('<I', (imm11_5 << 25) | (rs2 << 20) | (reg(rs1) << 15) | 
                             (funct3 << 12) | (imm4_0 << 7) | opcode)

        # Tipo B: BEQ, BNE, BGE, BLT
        elif instr in ['BEQ', 'BNE', 'BGE', 'BLT']:
            if len(tokens) != 4:
                raise ValueError(f"Formato inválido para {instr}: esperado RS1, RS2, LABEL")
            
            rs1, rs2 = reg(tokens[1]), reg(tokens[2])
            offset = (imm(tokens[3]) - pc) & 0x1FFF
            
            imm12 = (offset >> 12) & 0x1
            imm10_5 = (offset >> 5) & 0x3F
            imm4_1 = (offset >> 1) & 0xF
            imm11 = (offset >> 11) & 0x1
            
            funct3 = self.funct3_map[instr]
            opcode = self.opcode_map['B']
            
            return struct.pack('<I', (imm12 << 31) | (imm10_5 << 25) | (rs2 << 20) | 
                             (rs1 << 15) | (funct3 << 12) | (imm4_1 << 8) | 
                             (imm11 << 7) | opcode)

        # Tipo J: J, JAL
        elif instr in ['J', 'JAL']:
            if len(tokens) != 2 and len(tokens) != 3:
                raise ValueError(f"Formato inválido para {instr}: esperado [RD,] LABEL")
            
            # Determina se tem RD explícito ou não
            if len(tokens) == 2:
                # Formato: JAL LABEL (RD implícito como ra)
                label = tokens[1]
                rd = reg('ra') if instr == 'JAL' else 0
            else:
                # Formato: JAL RD, LABEL
                if instr == 'J':
                    raise ValueError("Instrução J não aceita RD explícito")
                rd = reg(tokens[1])
                label = tokens[2]
            
            try:
                offset = (labels[label] - pc) & 0x1FFFFF
            except KeyError:
                raise ValueError(f"Label não encontrado: {label}")

            # Extrai os bits do offset
            imm20 = (offset >> 20) & 0x1
            imm10_1 = (offset >> 1) & 0x3FF
            imm11 = (offset >> 11) & 0x1
            imm19_12 = (offset >> 12) & 0xFF
            
            opcode = self.opcode_map['J']
            
            return struct.pack('<I', (imm20 << 31) | (imm19_12 << 12) | (imm11 << 20) | 
                            (imm10_1 << 21) | (rd << 7) | opcode)
        else:
            raise ValueError(f"Instrução não suportada: {instr}")

    def montar(self, caminho_entrada, caminho_saida=None):
        """Função principal que realiza toda a montagem"""
        linhas = self.ler_arquivo(caminho_entrada)
        data_linhas, text_linhas = self.dividir_secoes(linhas)
        
        labels_data, memoria_data = self.processar_data(data_linhas)
        labels_text, instrucoes = self.primeira_passagem(text_linhas)
        labels = {**labels_data, **labels_text}
        
        memoria_text = bytearray()
        for pc, instr in instrucoes:
            try:
                codigo = self.montar_instrucao(instr, labels, pc)
                memoria_text += codigo
            except Exception as e:
                raise ValueError(f"Erro em PC={pc:04X}: {instr}\n{str(e)}")
        
        if not caminho_saida:
            caminho_saida = caminho_entrada.rsplit('.', 1)[0] + '.bin'
            
        with open(caminho_saida, 'wb') as f:
            f.write(memoria_data)
            f.write(memoria_text)
            
        return memoria_data, memoria_text


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Uso: python montador.py entrada.asm [saida.bin]")
        sys.exit(1)
        
    montador = Montador()
    try:
        montador.montar(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
        print("Montagem concluída com sucesso!")
    except Exception as e:
        print(f"Erro durante a montagem: {str(e)}")
        sys.exit(1)