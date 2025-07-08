import struct

class Simulador:

    def __init__ (self, file_data, file_text):
        self.bancoReg = [0]*32
        self.memoria_dados = self.carregar_memoria(file_data)
        self.instrucoes = self.carregar_instrucoes(file_text)
        self.pc = 0 
        self.ciclo = 0

        self.IF_ID = {}
        self.ID_EX = {}
        self.EX_MEM = {}
        self.MEM_WB = {}

        self.fim = False

    def carregar_memoria(self, file_path):
        with open(file_path, 'rb') as f:
            dados_binarios = f.read()
        memoria = {}
        for i in range(0, len(dados_binarios), 4):
            endereco = i
            valor = struct.unpack('<i', dados_binarios[i:i+4])[0]
            memoria[endereco] = valor
        return memoria
    
    def carregar_instrucoes(self, file_path):
        with open(file_path, 'rb') as f:
            dados_binarios = f.read()
        instrucoes = []
        for i in range(0, len(dados_binarios), 4):
            instr = struct.unpack('<I', dados_binarios[i:i+4])[0]
            instrucoes.append(instr)
        return instrucoes
    

    # etapas --------------------------------------------------

    def etapa_IF (self):
        if self.pc >= len(self.instrucoes) * 4:
            self.fim = True
            self.IF_ID = {}
            return None
        
        instrucao = self.instrucoes[self.pc // 4]
        self.IF_ID = {'instrucao': instrucao, 'pc': self.pc}
        self.pc += 4


    def etapa_ID (self):
        if not self.IF_ID:
            self.ID_EX = {}
            return None
        
        instr = self.IF_ID['instrucao']
        opcode = instr & 0x7F

        if opcode == 0b0110011:  # Tipo R
            self.ID_EX = {
                'tipo': 'R',
                'rd': (instr >> 7) & 0x1F,
                'funct3': (instr >> 12) & 0x7,
                'rs1': (instr >> 15) & 0x1F,
                'rs2': (instr >> 20) & 0x1F,
                'funct7': (instr >> 25) & 0x7F
            }

        elif opcode == 0b0010011:  # Tipo I (ex: ADDI)
            imm = (instr >> 20) & 0xFFF
            imm = imm - 4096 if imm & 0x800 else imm
            self.ID_EX = {
                'tipo': 'I',
                'rd': (instr >> 7) & 0x1F,
                'funct3': (instr >> 12) & 0x7,
                'rs1': (instr >> 15) & 0x1F,
                'imm': imm
            }

        elif opcode == 0b0000011:  # LW
            imm = (instr >> 20) & 0xFFF
            imm = imm - 4096 if imm & 0x800 else imm
            self.ID_EX = {
                'tipo': 'LW',
                'rd': (instr >> 7) & 0x1F,
                'funct3': (instr >> 12) & 0x7,
                'rs1': (instr >> 15) & 0x1F,
                'imm': imm
            }

        elif opcode == 0b0100011:  # SW
            imm11_5 = (instr >> 25) & 0x7F
            imm4_0 = (instr >> 7) & 0x1F
            imm = (imm11_5 << 5) | imm4_0
            imm = imm - 4096 if imm & 0x800 else imm
            self.ID_EX = {
                'tipo': 'SW',
                'funct3': (instr >> 12) & 0x7,
                'rs1': (instr >> 15) & 0x1F,
                'rs2': (instr >> 20) & 0x1F,
                'imm': imm
            }

        elif opcode == 0b1100011:  # BEQ, BNE (Tipo B)
            imm12 = (instr >> 31) & 0x1
            imm10_5 = (instr >> 25) & 0x3F
            imm4_1 = (instr >> 8) & 0xF
            imm11 = (instr >> 7) & 0x1
            imm = (imm12 << 12) | (imm11 << 11) | (imm10_5 << 5) | (imm4_1 << 1)
            imm = imm - 8192 if imm & 0x1000 else imm
            self.ID_EX = {
                'tipo': 'B',
                'funct3': (instr >> 12) & 0x7,
                'rs1': (instr >> 15) & 0x1F,
                'rs2': (instr >> 20) & 0x1F,
                'imm': imm,
                'pc': self.IF_ID['pc']
            }

        elif opcode == 0b1101111:  # JAL (Tipo J)
            rd = (instr >> 7) & 0x1F
            imm = (
                ((instr >> 31) & 0x1) << 20 |
                ((instr >> 21) & 0x3FF) << 1 |
                ((instr >> 20) & 0x1) << 11 |
                ((instr >> 12) & 0xFF) << 12
            )
            imm = imm - (1 << 21) if imm & (1 << 20) else imm
            self.ID_EX = {
                'tipo': 'J',
                'rd': rd,
                'imm': imm,
                'pc': self.IF_ID['pc']
            }

        else:
            print("opcode não suportado!")
            self.ID_EX = {}


    def etapa_EX (self):
        if not self.ID_EX:
            self.EX_MEM = {}
            return None
        
        tipo = self.ID_EX['tipo']

        if tipo == 'R':
            rs1 = self.bancoReg[self.ID_EX['rs1']]
            rs2 = self.bancoReg[self.ID_EX['rs2']]
            funct3 = self.ID_EX['funct3']
            funct7 = self.ID_EX['funct7']

            if funct3 == 0b000:
                if funct7 == 0b0000000:
                    resultado = rs1 + rs2  # ADD
                elif funct7 == 0b0100000:
                    resultado = rs1 - rs2  # SUB
                elif funct7 == 0b0000001:
                    resultado = rs1 * rs2  # MUL
                else:
                    resultado = 0
            elif funct3 == 0b100:
                resultado = rs1 ^ rs2  # XOR
            elif funct3 == 0b110:
                resultado = rs1 | rs2  # OR
            elif funct3 == 0b111:
                resultado = rs1 & rs2  # AND
            elif funct3 == 0b001:
                resultado = rs1 << (rs2 & 0x1F)  # SLL
            elif funct3 == 0b101:
                resultado = rs1 >> (rs2 & 0x1F)  # SRL
            elif funct3 == 0b100 and funct7 == 0b0000001:
                resultado = rs1 % rs2  # REM
            elif funct3 == 0b100 and funct7 == 0b0000001:
                resultado = rs1 // rs2  # DIV
            else:
                resultado = 0

            self.EX_MEM = {'tipo': 'R', 'rd': self.ID_EX['rd'], 'resultado': resultado}


        elif tipo == 'I':
            rs1 = self.bancoReg[self.ID_EX['rs1']]
            imm = self.ID_EX['imm']
            resultado = rs1 + imm
            self.EX_MEM = {'tipo': 'I', 'rd': self.ID_EX['rd'], 'resultado': resultado}


        elif tipo == 'LW':
            rs1 = self.bancoReg[self.ID_EX['rs1']]
            endereco = rs1 + self.ID_EX['imm']
            self.EX_MEM = {'tipo': 'LW', 'rd': self.ID_EX['rd'], 'endereco': endereco}

        elif tipo == 'SW':

            rs1 = self.bancoReg[self.ID_EX['rs1']]
            rs2 = self.bancoReg[self.ID_EX['rs2']]
            endereco = rs1 + self.ID_EX['imm']
            self.EX_MEM = {'tipo': 'SW', 'rs2_valor': rs2, 'endereco': endereco}

        elif tipo == 'B':

            rs1 = self.bancoReg[self.ID_EX['rs1']]
            rs2 = self.bancoReg[self.ID_EX['rs2']]
            desvia = False
            if self.ID_EX['funct3'] == 0b000 and rs1 == rs2:  # BEQ
                desvia = True
            elif self.ID_EX['funct3'] == 0b001 and rs1 != rs2:  # BNE
                desvia = True
            self.EX_MEM = {'tipo': 'B', 'desvia': desvia, 'novo_pc': self.ID_EX['pc'] + self.ID_EX['imm']}
            

        elif tipo == 'J':
            self.EX_MEM = {
                'tipo': 'J',
                'rd': self.ID_EX['rd'],
                'pc_retorno': self.ID_EX['pc'] + 4,
                'novo_pc': self.ID_EX['pc'] + self.ID_EX['imm']
            }


    def etapa_MEM (self):
        if not self.EX_MEM:
            self.MEM_WB = {}
            return None
        
        tipo = self.EX_MEM['tipo']

        if tipo == 'LW':
            val = self.memoria_dados.get(self.EX_MEM['endereco'], 0)
            self.MEM_WB = {'tipo': 'LW', 'rd': self.EX_MEM['rd'], 'resultado': val}

        elif tipo == 'SW':
            self.memoria_dados[self.EX_MEM['endereco']] = self.EX_MEM['rs2_valor']
            self.MEM_WB = {'tipo': 'SW'}

        elif tipo in ['R', 'I']:
            self.MEM_WB = self.EX_MEM

        elif tipo == 'B':
            if self.EX_MEM['desvia']:
                self.pc = self.EX_MEM['novo_pc']
                self.IF_ID = {} 
            self.MEM_WB = {'tipo': 'B'}

        elif tipo == 'J':
            self.bancoReg[self.EX_MEM['rd']] = self.EX_MEM['pc_retorno']
            self.pc = self.EX_MEM['novo_pc']
            self.IF_ID = {}
            self.MEM_WB = {'tipo': 'J'}

        
    def etapa_WB (self):
        if not self.MEM_WB:
            return None
        
        tipo = self.MEM_WB['tipo']
        if tipo in ['R', 'I', 'LW']:
            rd = self.MEM_WB['rd']
            if rd != 0:
                self.bancoReg[rd] = self.MEM_WB['resultado']


    # execução -------------------------------------------


    def executar_ciclo(self):
        self.etapa_WB()
        self.etapa_MEM()
        self.etapa_EX()
        self.etapa_ID()
        self.etapa_IF()
        self.ciclo += 1

    def exibir_estado(self):
        print("Registradores:")
        for i in range(0, 32, 8):
            print("  " + "  ".join([f"x{j:<2}={self.bancoReg[j]:<5}" for j in range(i, i+8)]))
        print("PC:", self.pc)

    
    def executar(self):
        self.IF_ID = {}
        self.ID_EX = {}
        self.EX_MEM = {}
        self.MEM_WB = {}

        while self.ciclo < 10000:
            print(f"\nCiclo {self.ciclo}")      
            self.executar_ciclo()
            self.exibir_estado()

            if (
                self.pc >= len(self.instrucoes) * 4 and
                not self.IF_ID and
                not self.ID_EX and
                not self.EX_MEM and
                not self.MEM_WB
            ):
                break


sim = Simulador('Teste_data.bin', 'Teste_text.bin')
sim.executar()
