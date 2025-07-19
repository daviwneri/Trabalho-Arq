import struct

class Simulador:

    def __init__ (self, file_data, file_text, opcoes_extras=None):
        self.bancoReg = [0]*32

        if file_data is not None:
            self.memoria_dados = self.carregar_memoria(file_data)
        else:
            self.memoria_dados = {} 

        self.instrucoes = self.carregar_instrucoes(file_text)
        self.pc = 0 
        self.ciclo = 0

        self.IF_ID = {}
        self.ID_EX = {}
        self.EX_MEM = {}
        self.MEM_WB = {}

        self.fim = False
        
        # Configurações das funcionalidades extras
        if opcoes_extras is None:
            opcoes_extras = {}
        
        self.previsao_desvio_habilitada = opcoes_extras.get('previsao_desvio', False)
        self.forwarding_habilitado = opcoes_extras.get('forwarding', False)
        self.deteccao_hazards_habilitada = opcoes_extras.get('deteccao_hazards', False)
        
        # Sistema de previsão de desvio de 2 bits
        self.tabela_previsao = {}  # PC -> estado (0=strongly not taken, 1=weakly not taken, 2=weakly taken, 3=strongly taken)
        self.pc_desvio_previsto = None
        self.desvio_foi_tomado = False
        
        # Contadores para estatísticas
        self.desvios_corretos = 0
        self.desvios_incorretos = 0
        self.stalls_por_hazard = 0
        self.forwards_realizados = 0
        
        # Pipeline com informações extras para forwarding/hazards
        self.pipeline_info = {
            'IF': {'vazio': True, 'instrucao': None, 'pc': None},
            'ID': {'vazio': True, 'instrucao': None, 'rs1': None, 'rs2': None, 'rd': None},
            'EX': {'vazio': True, 'instrucao': None, 'rd': None, 'resultado': None},
            'MEM': {'vazio': True, 'instrucao': None, 'rd': None, 'resultado': None},
            'WB': {'vazio': True, 'instrucao': None, 'rd': None, 'resultado': None}
        }
        
        # Flag para stall
        self.stall = False

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
    
    def instrucao_para_assembly(self, data_dict):
        """Converte dados de instrução decodificada para formato assembly"""
        if not data_dict or 'tipo' not in data_dict:
            return ""
            
        tipo = data_dict['tipo']
        
        if tipo == 'R':
            # Instruções tipo R: ADD, SUB, AND, OR, etc.
            funct3 = data_dict.get('funct3', 0)
            funct7 = data_dict.get('funct7', 0)
            rd = data_dict.get('rd', 0)
            rs1 = data_dict.get('rs1', 0)
            rs2 = data_dict.get('rs2', 0)
            
            if funct3 == 0 and funct7 == 0:
                return f"ADD x{rd}, x{rs1}, x{rs2}"
            elif funct3 == 0 and funct7 == 32:
                return f"SUB x{rd}, x{rs1}, x{rs2}"
            elif funct3 == 7:
                return f"AND x{rd}, x{rs1}, x{rs2}"
            elif funct3 == 6:
                return f"OR x{rd}, x{rs1}, x{rs2}"
            else:
                return f"R-type x{rd}, x{rs1}, x{rs2}"
                
        elif tipo == 'I':
            # Instruções tipo I: ADDI, etc.
            funct3 = data_dict.get('funct3', 0)
            rd = data_dict.get('rd', 0)
            rs1 = data_dict.get('rs1', 0)
            imm = data_dict.get('imm', 0)
            
            if funct3 == 0:
                return f"ADDI x{rd}, x{rs1}, {imm}"
            else:
                return f"I-type x{rd}, x{rs1}, {imm}"
                
        elif tipo == 'LW':
            rd = data_dict.get('rd', 0)
            rs1 = data_dict.get('rs1', 0)
            imm = data_dict.get('imm', 0)
            return f"LW x{rd}, {imm}(x{rs1})"
            
        elif tipo == 'SW':
            rs1 = data_dict.get('rs1', 0)
            rs2 = data_dict.get('rs2', 0)
            imm = data_dict.get('imm', 0)
            return f"SW x{rs2}, {imm}(x{rs1})"
            
        elif tipo == 'B':
            funct3 = data_dict.get('funct3', 0)
            rs1 = data_dict.get('rs1', 0)
            rs2 = data_dict.get('rs2', 0)
            imm = data_dict.get('imm', 0)
            
            if funct3 == 0:
                return f"BEQ x{rs1}, x{rs2}, {imm}"
            elif funct3 == 1:
                return f"BNE x{rs1}, x{rs2}, {imm}"
            else:
                return f"B-type x{rs1}, x{rs2}, {imm}"
                
        elif tipo == 'J':
            rd = data_dict.get('rd', 0)
            imm = data_dict.get('imm', 0)
            return f"JAL x{rd}, {imm}"
            
        return f"{tipo}-type"
    
    # ============= FUNCIONALIDADES EXTRAS =============
    
    def prever_desvio(self, pc_branch):
        """Previsão de desvio de 2 bits"""
        if not self.previsao_desvio_habilitada:
            return False
            
        estado = self.tabela_previsao.get(pc_branch, 1)  # Default: weakly not taken
        return estado >= 2  # taken se estado >= 2
    
    def atualizar_previsao(self, pc_branch, desvio_tomado):
        """Atualiza tabela de previsão de 2 bits"""
        if not self.previsao_desvio_habilitada:
            return
            
        estado_atual = self.tabela_previsao.get(pc_branch, 1)
        
        if desvio_tomado:
            # Desvio foi tomado - incrementa (máximo 3)
            novo_estado = min(3, estado_atual + 1)
        else:
            # Desvio não foi tomado - decrementa (mínimo 0)
            novo_estado = max(0, estado_atual - 1)
            
        self.tabela_previsao[pc_branch] = novo_estado
    
    def flush_pipeline(self):
        """Faz flush do pipeline em caso de previsão incorreta"""
        self.IF_ID = {}
        self.ID_EX = {}
        # EX_MEM e MEM_WB não são afetados pelo flush
        
        # Atualiza informações do pipeline
        self.pipeline_info['IF']['vazio'] = True
        self.pipeline_info['ID']['vazio'] = True
    
    def detectar_hazard_dados(self):
        """Detecta hazards de dados RAW (Read After Write)"""
        if not self.deteccao_hazards_habilitada:
            return False
            
        # Se não há instrução em ID, não há hazard
        if not self.ID_EX:
            return False
            
        # Registradores que a instrução atual precisa ler
        rs1 = self.ID_EX.get('rs1')
        rs2 = self.ID_EX.get('rs2') 
        
        # Verifica hazard com EX (1 ciclo atrás)
        if self.EX_MEM and self.EX_MEM.get('rd') is not None:
            rd_ex = self.EX_MEM['rd']
            if rd_ex != 0 and (rd_ex == rs1 or rd_ex == rs2):
                # Hazard detectado - verifica se pode ser resolvido com forwarding
                if self.forwarding_habilitado and self.EX_MEM['tipo'] != 'LW':
                    return False  # Forwarding resolve
                return True
        
        # Verifica hazard com MEM (2 ciclos atrás)  
        if self.MEM_WB and self.MEM_WB.get('rd') is not None:
            rd_mem = self.MEM_WB['rd']
            if rd_mem != 0 and (rd_mem == rs1 or rd_mem == rs2):
                # Hazard detectado
                if self.forwarding_habilitado:
                    return False  # Forwarding resolve
                return True
                
        # Hazard especial: LW seguido de uso (necessita stall mesmo com forwarding)
        if self.EX_MEM and self.EX_MEM.get('tipo') == 'LW':
            rd_lw = self.EX_MEM.get('rd')
            if rd_lw != 0 and (rd_lw == rs1 or rd_lw == rs2):
                return True  # LW hazard sempre causa stall
                
        return False
    
    def realizar_forwarding(self):
        """Implementa forwarding dos resultados"""
        if not self.forwarding_habilitado or not self.ID_EX:
            return
            
        rs1_val = self.bancoReg[self.ID_EX.get('rs1', 0)]
        rs2_val = self.bancoReg[self.ID_EX.get('rs2', 0)]
        forwarding_realizado = False
        
        # Forward de EX/MEM para EX (EX-EX forwarding)
        if self.EX_MEM and self.EX_MEM.get('rd') is not None and self.EX_MEM['rd'] != 0:
            rd_ex = self.EX_MEM['rd']
            resultado_ex = self.EX_MEM.get('resultado')
            
            if resultado_ex is not None:
                if rd_ex == self.ID_EX.get('rs1'):
                    rs1_val = resultado_ex
                    forwarding_realizado = True
                if rd_ex == self.ID_EX.get('rs2'):
                    rs2_val = resultado_ex
                    forwarding_realizado = True
        
        # Forward de MEM/WB para EX (MEM-EX forwarding)  
        if self.MEM_WB and self.MEM_WB.get('rd') is not None and self.MEM_WB['rd'] != 0:
            rd_mem = self.MEM_WB['rd']
            resultado_mem = self.MEM_WB.get('resultado')
            
            if resultado_mem is not None:
                # Só faz forward se EX/MEM não já forneceu o dado
                if rd_mem == self.ID_EX.get('rs1') and (not self.EX_MEM or self.EX_MEM.get('rd') != rd_mem):
                    rs1_val = resultado_mem
                    forwarding_realizado = True
                if rd_mem == self.ID_EX.get('rs2') and (not self.EX_MEM or self.EX_MEM.get('rd') != rd_mem):
                    rs2_val = resultado_mem
                    forwarding_realizado = True
        
        # Atualiza os valores no pipeline para uso no EX
        if 'rs1_val_forward' not in self.ID_EX:
            self.ID_EX['rs1_val_forward'] = rs1_val
            self.ID_EX['rs2_val_forward'] = rs2_val
            
        if forwarding_realizado:
            self.forwards_realizados += 1
    
    def inserir_stall(self):
        """Insere um stall (bolha) no pipeline"""
        # Mantém IF_ID, mas impede ID de progredir
        # ID_EX recebe uma bolha (NOP)
        self.ID_EX = {'tipo': 'NOP', 'stall': True}
        self.stalls_por_hazard += 1
        self.stall = True
        
        # Não avança o PC
        self.pc -= 4
    
    def obter_estatisticas(self):
        """Retorna estatísticas das funcionalidades extras"""
        total_desvios = self.desvios_corretos + self.desvios_incorretos
        taxa_acerto = (self.desvios_corretos / total_desvios * 100) if total_desvios > 0 else 0
        
        return {
            'previsao_desvio': {
                'habilitada': self.previsao_desvio_habilitada,
                'desvios_corretos': self.desvios_corretos,
                'desvios_incorretos': self.desvios_incorretos,
                'taxa_acerto': taxa_acerto
            },
            'forwarding': {
                'habilitado': self.forwarding_habilitado,
                'forwards_realizados': self.forwards_realizados
            },
            'hazards': {
                'deteccao_habilitada': self.deteccao_hazards_habilitada,
                'stalls_por_hazard': self.stalls_por_hazard
            }
        }
    

    # etapas --------------------------------------------------

    def etapa_IF (self):
        # Se há stall, não busca nova instrução
        if self.stall:
            self.stall = False  # Remove stall para próximo ciclo
            return
            
        if self.pc >= len(self.instrucoes) * 4:
            self.fim = True
            self.IF_ID = {}
            self.pipeline_info['IF']['vazio'] = True
            return None
        
        instrucao = self.instrucoes[self.pc // 4]
        self.IF_ID = {'instrucao': instrucao, 'pc': self.pc}
        
        # Atualiza informações do pipeline
        self.pipeline_info['IF'] = {
            'vazio': False,
            'instrucao': instrucao,
            'pc': self.pc
        }
        
        self.pc += 4


    def etapa_ID (self):
        if not self.IF_ID:
            self.ID_EX = {}
            self.pipeline_info['ID']['vazio'] = True
            return None
        
        # Detecta hazards de dados antes de decodificar
        if self.detectar_hazard_dados():
            self.inserir_stall()
            return
        
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

        elif opcode == 0b0010011:  # Tipo I (ex: ADDI, SLLI, SRLI)
            imm = (instr >> 20) & 0xFFF
            imm = imm - 4096 if imm & 0x800 else imm
            self.ID_EX = {
                'tipo': 'I',
                'rd': (instr >> 7) & 0x1F,
                'funct3': (instr >> 12) & 0x7,
                'rs1': (instr >> 15) & 0x1F,
                'imm': imm
            }

        elif opcode == 0b1100111:  # JALR
            imm = (instr >> 20) & 0xFFF
            imm = imm - 4096 if imm & 0x800 else imm
            self.ID_EX = {
                'tipo': 'JALR',
                'rd': (instr >> 7) & 0x1F,
                'rs1': (instr >> 15) & 0x1F,
                'imm': imm,
                'pc': self.IF_ID['pc']
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
            
            # Previsão de desvio
            if self.previsao_desvio_habilitada:
                pc_branch = self.IF_ID['pc']
                previsao = self.prever_desvio(pc_branch)
                self.ID_EX['previsao'] = previsao
                if previsao:
                    # Prevê que desvio será tomado - especula
                    self.pc_desvio_previsto = pc_branch + imm
                    self.pc = self.pc_desvio_previsto

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
            
        # Atualiza informações do pipeline
        if self.ID_EX:
            self.pipeline_info['ID'] = {
                'vazio': False,
                'instrucao': self.ID_EX.get('tipo', 'UNKNOWN'),
                'rs1': self.ID_EX.get('rs1'),
                'rs2': self.ID_EX.get('rs2'),
                'rd': self.ID_EX.get('rd')
            }
        else:
            self.pipeline_info['ID']['vazio'] = True


    def etapa_EX (self):
        if not self.ID_EX:
            self.EX_MEM = {}
            self.pipeline_info['EX']['vazio'] = True
            return None
        
        # Se é um stall (bolha), não executa nada
        if self.ID_EX.get('stall'):
            self.EX_MEM = {'tipo': 'NOP', 'stall': True}
            self.pipeline_info['EX'] = {'vazio': False, 'instrucao': 'STALL', 'rd': None, 'resultado': None}
            return
        
        # Realiza forwarding antes da execução
        self.realizar_forwarding()
        
        tipo = self.ID_EX['tipo']

        if tipo == 'R':
            # Usa valores com forwarding se disponíveis
            rs1 = self.ID_EX.get('rs1_val_forward', self.bancoReg[self.ID_EX['rs1']])
            rs2 = self.ID_EX.get('rs2_val_forward', self.bancoReg[self.ID_EX['rs2']])
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
            elif funct3 == 0b110 and funct7 == 0b0000001:
                resultado = rs1 % rs2  # REM
            elif funct3 == 0b100 and funct7 == 0b0000001:
                resultado = rs1 // rs2  # DIV
            else:
                resultado = 0

            self.EX_MEM = {'tipo': 'R', 'rd': self.ID_EX['rd'], 'resultado': resultado}

        elif tipo == 'I':
            rs1 = self.ID_EX.get('rs1_val_forward', self.bancoReg[self.ID_EX['rs1']])
            imm = self.ID_EX['imm']
            funct3 = self.ID_EX.get('funct3', 0)
            
            if funct3 == 0b000:  # ADDI
                resultado = rs1 + imm
            elif funct3 == 0b001:  # SLLI
                resultado = rs1 << (imm & 0x1F)
            elif funct3 == 0b101:  # SRLI
                resultado = rs1 >> (imm & 0x1F)
            else:
                resultado = rs1 + imm  # Default para ADDI
                
            self.EX_MEM = {'tipo': 'I', 'rd': self.ID_EX['rd'], 'resultado': resultado}

        elif tipo == 'LW':
            rs1 = self.ID_EX.get('rs1_val_forward', self.bancoReg[self.ID_EX['rs1']])
            endereco = rs1 + self.ID_EX['imm']
            self.EX_MEM = {'tipo': 'LW', 'rd': self.ID_EX['rd'], 'endereco': endereco}

        elif tipo == 'SW':
            rs1 = self.ID_EX.get('rs1_val_forward', self.bancoReg[self.ID_EX['rs1']])
            rs2 = self.ID_EX.get('rs2_val_forward', self.bancoReg[self.ID_EX['rs2']])
            endereco = rs1 + self.ID_EX['imm']
            self.EX_MEM = {'tipo': 'SW', 'rs2_valor': rs2, 'endereco': endereco}

        elif tipo == 'B':
            rs1 = self.ID_EX.get('rs1_val_forward', self.bancoReg[self.ID_EX['rs1']])
            rs2 = self.ID_EX.get('rs2_val_forward', self.bancoReg[self.ID_EX['rs2']])
            desvia = False

            if self.ID_EX['funct3'] == 0b000 and rs1 == rs2:  # BEQ
                desvia = True
            elif self.ID_EX['funct3'] == 0b001 and rs1 != rs2:  # BNE
                desvia = True
            elif self.ID_EX['funct3'] == 0b100 and rs1 < rs2:   # BLT
                desvia = True
            elif self.ID_EX['funct3'] == 0b101 and rs1 >= rs2:  # BGE
                desvia = True
                
            self.EX_MEM = {'tipo': 'B', 'desvia': desvia, 'novo_pc': self.ID_EX['pc'] + self.ID_EX['imm']}
            
            # Verificar previsão de desvio
            if self.previsao_desvio_habilitada and 'previsao' in self.ID_EX:
                previsao = self.ID_EX['previsao']
                pc_branch = self.ID_EX['pc']
                
                # Atualiza tabela de previsão
                self.atualizar_previsao(pc_branch, desvia)
                
                # Verifica se previsão estava correta
                if previsao == desvia:
                    self.desvios_corretos += 1
                else:
                    self.desvios_incorretos += 1
                    # Previsão incorreta - fazer flush e corrigir PC
                    if previsao and not desvia:
                        # Previu taken mas não tomou - voltar
                        self.pc = self.ID_EX['pc'] + 4
                    elif not previsao and desvia:
                        # Previu not taken mas tomou - ir para destino
                        self.pc = self.ID_EX['pc'] + self.ID_EX['imm']
                    self.flush_pipeline()
            
        elif tipo == 'JALR':
            rs1 = self.ID_EX.get('rs1_val_forward', self.bancoReg[self.ID_EX['rs1']])
            novo_pc = (rs1 + self.ID_EX['imm']) & ~1  # Alinha para palavra
            self.EX_MEM = {
                'tipo': 'JALR',
                'rd': self.ID_EX['rd'],
                'pc_retorno': self.ID_EX['pc'] + 4,
                'novo_pc': novo_pc
            }

        elif tipo == 'J':
            self.EX_MEM = {
                'tipo': 'J',
                'rd': self.ID_EX['rd'],
                'pc_retorno': self.ID_EX['pc'] + 4,
                'novo_pc': self.ID_EX['pc'] + self.ID_EX['imm']
            }
            
        # Atualiza informações do pipeline
        if self.EX_MEM and not self.EX_MEM.get('stall'):
            self.pipeline_info['EX'] = {
                'vazio': False,
                'instrucao': self.EX_MEM.get('tipo', 'UNKNOWN'),
                'rd': self.EX_MEM.get('rd'),
                'resultado': self.EX_MEM.get('resultado')
            }
        else:
            self.pipeline_info['EX']['vazio'] = True


    def etapa_MEM (self):
        if not self.EX_MEM:
            self.MEM_WB = {}
            self.pipeline_info['MEM']['vazio'] = True
            return None
        
        # Se é um stall (bolha), passa adiante
        if self.EX_MEM.get('stall'):
            self.MEM_WB = {'tipo': 'NOP', 'stall': True}
            self.pipeline_info['MEM'] = {'vazio': False, 'instrucao': 'STALL', 'rd': None, 'resultado': None}
            return
        
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
            # Se não houver previsão de desvio, comportamento normal
            if not self.previsao_desvio_habilitada:
                if self.EX_MEM['desvia']:
                    self.pc = self.EX_MEM['novo_pc']
                    self.IF_ID = {}
                    self.ID_EX = {}
            self.MEM_WB = {'tipo': 'B'}

        elif tipo == 'J':
            if self.EX_MEM['rd'] != 0:
                self.bancoReg[self.EX_MEM['rd']] = self.EX_MEM['pc_retorno']
            self.pc = self.EX_MEM['novo_pc']
            self.IF_ID = {}
            self.ID_EX = {}
            self.MEM_WB = {'tipo': 'J'}

        elif tipo == 'JALR':
            if self.EX_MEM['rd'] != 0:
                self.bancoReg[self.EX_MEM['rd']] = self.EX_MEM['pc_retorno']
            self.pc = self.EX_MEM['novo_pc']
            self.IF_ID = {}
            self.ID_EX = {}
            self.MEM_WB = {'tipo': 'JALR'}
            
        # Atualiza informações do pipeline
        if self.MEM_WB and not self.MEM_WB.get('stall'):
            self.pipeline_info['MEM'] = {
                'vazio': False,
                'instrucao': self.MEM_WB.get('tipo', 'UNKNOWN'),
                'rd': self.MEM_WB.get('rd'),
                'resultado': self.MEM_WB.get('resultado')
            }
        else:
            self.pipeline_info['MEM']['vazio'] = True

        
    def etapa_WB (self):
        if not self.MEM_WB:
            self.pipeline_info['WB']['vazio'] = True
            return None
        
        # Se é um stall (bolha), não faz nada
        if self.MEM_WB.get('stall'):
            self.pipeline_info['WB'] = {'vazio': False, 'instrucao': 'STALL', 'rd': None, 'resultado': None}
            return
        
        tipo = self.MEM_WB['tipo']
        if tipo in ['R', 'I', 'LW']:
            rd = self.MEM_WB['rd']
            if rd != 0:
                self.bancoReg[rd] = self.MEM_WB['resultado']
                
        # Atualiza informações do pipeline
        if self.MEM_WB:
            self.pipeline_info['WB'] = {
                'vazio': False,
                'instrucao': self.MEM_WB.get('tipo', 'UNKNOWN'),
                'rd': self.MEM_WB.get('rd'),
                'resultado': self.MEM_WB.get('resultado')
            }
        else:
            self.pipeline_info['WB']['vazio'] = True


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
        print("MEM_Dados:", self.memoria_dados)
        print("PC:", self.pc)


    def executar(self, mostrar_detalhes=True):
        self.IF_ID = {}
        self.ID_EX = {}
        self.EX_MEM = {}
        self.MEM_WB = {}

        while self.ciclo < 10000:
            if mostrar_detalhes:
                print(f"\nCiclo {self.ciclo}")      
            self.executar_ciclo()
            if mostrar_detalhes:
                self.exibir_estado()

            if (
                self.pc >= len(self.instrucoes) * 4 and
                not self.IF_ID and
                not self.ID_EX and
                not self.EX_MEM and
                not self.MEM_WB
            ):
                break
                
        # Exibe estatísticas das funcionalidades extras
        if mostrar_detalhes:
            self.exibir_estatisticas()
            
    def exibir_estatisticas(self):
        """Exibe estatísticas das funcionalidades extras"""
        print("\n" + "="*50)
        print("ESTATÍSTICAS DAS FUNCIONALIDADES EXTRAS")
        print("="*50)
        
        stats = self.obter_estatisticas()
        
        # Previsão de desvio
        pred_stats = stats['previsao_desvio']
        print(f"Previsão de Desvio: {'HABILITADA' if pred_stats['habilitada'] else 'DESABILITADA'}")
        if pred_stats['habilitada']:
            print(f"  - Desvios corretos: {pred_stats['desvios_corretos']}")
            print(f"  - Desvios incorretos: {pred_stats['desvios_incorretos']}")
            print(f"  - Taxa de acerto: {pred_stats['taxa_acerto']:.1f}%")
        
        # Forwarding
        fwd_stats = stats['forwarding']
        print(f"Forwarding: {'HABILITADO' if fwd_stats['habilitado'] else 'DESABILITADO'}")
        if fwd_stats['habilitado']:
            print(f"  - Forwards realizados: {fwd_stats['forwards_realizados']}")
        
        # Detecção de hazards
        haz_stats = stats['hazards']
        print(f"Detecção de Hazards: {'HABILITADA' if haz_stats['deteccao_habilitada'] else 'DESABILITADA'}")
        if haz_stats['deteccao_habilitada']:
            print(f"  - Stalls por hazard: {haz_stats['stalls_por_hazard']}")
            
        print("="*50)


