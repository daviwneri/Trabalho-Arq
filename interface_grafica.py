import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import struct
from montador import Montador
from simulador import Simulador

class InterfaceSimuladorRISCV:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador RISC-V com Pipeline - Funcionalidades Extras")
        self.root.geometry("1500x1000")
        
        # Estado do simulador
        self.simulador = None
        self.montador = Montador()
        self.arquivo_asm = None
        self.arquivo_bin = None
        self.executando = False
        self.arquivo_saida = None
        self.wb_buffer = {}  # Buffer para rastrear o que está no estágio WB
        
        # Variáveis para funcionalidades extras
        self.var_previsao_desvio = tk.BooleanVar(value=False)
        self.var_forwarding = tk.BooleanVar(value=False)
        self.var_deteccao_hazards = tk.BooleanVar(value=False)
        
        # Configurar interface
        self.setup_interface()
        
    def setup_interface(self):
        # Menu principal
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Abrir arquivo .asm", command=self.abrir_arquivo)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        
        # Menu de configurações
        config_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Configurações", menu=config_menu)
        config_menu.add_checkbutton(label="Previsão de Desvio", variable=self.var_previsao_desvio, command=self.atualizar_configuracoes)
        config_menu.add_checkbutton(label="Forwarding", variable=self.var_forwarding, command=self.atualizar_configuracoes)
        config_menu.add_checkbutton(label="Detecção de Hazards", variable=self.var_deteccao_hazards, command=self.atualizar_configuracoes)
        
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame superior - controles
        control_frame = ttk.LabelFrame(main_frame, text="Controles", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Frame para funcionalidades extras
        extras_frame = ttk.LabelFrame(control_frame, text="Funcionalidades Extras", padding=5)
        extras_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Checkboxes para funcionalidades extras
        cb_frame = ttk.Frame(extras_frame)
        cb_frame.pack(fill=tk.X)
        
        self.cb_previsao = ttk.Checkbutton(cb_frame, text="Previsão de Desvio (2 bits)", 
                                          variable=self.var_previsao_desvio, command=self.atualizar_configuracoes)
        self.cb_previsao.pack(side=tk.LEFT, padx=(0, 20))
        
        self.cb_forwarding = ttk.Checkbutton(cb_frame, text="Forwarding", 
                                            variable=self.var_forwarding, command=self.atualizar_configuracoes)
        self.cb_forwarding.pack(side=tk.LEFT, padx=(0, 20))
        
        self.cb_hazards = ttk.Checkbutton(cb_frame, text="Detecção de Hazards", 
                                         variable=self.var_deteccao_hazards, command=self.atualizar_configuracoes)
        self.cb_hazards.pack(side=tk.LEFT, padx=(0, 20))
        
        # Botões de controle
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X)
        
        self.btn_carregar = ttk.Button(btn_frame, text="Carregar Arquivo", command=self.abrir_arquivo)
        self.btn_carregar.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_executar = ttk.Button(btn_frame, text="Executar Próximo Ciclo", command=self.executar_ciclo, state=tk.DISABLED)
        self.btn_executar.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_executar_tudo = ttk.Button(btn_frame, text="Executar Tudo", command=self.executar_tudo, state=tk.DISABLED)
        self.btn_executar_tudo.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_reset = ttk.Button(btn_frame, text="Reset", command=self.reset_simulador, state=tk.DISABLED)
        self.btn_reset.pack(side=tk.LEFT, padx=(0, 10))
        
        # Info do arquivo
        info_frame = ttk.Frame(control_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(info_frame, text="Arquivo:").pack(side=tk.LEFT)
        self.lbl_arquivo = ttk.Label(info_frame, text="Nenhum arquivo carregado", foreground="gray")
        self.lbl_arquivo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Ciclo atual
        ttk.Label(info_frame, text="Ciclo:").pack(side=tk.LEFT, padx=(30, 0))
        self.lbl_ciclo = ttk.Label(info_frame, text="0", font=("Arial", 10, "bold"))
        self.lbl_ciclo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Notebook para as abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba 1: Pipeline
        self.setup_pipeline_tab()
        
        # Aba 2: Registradores
        self.setup_registradores_tab()
        
        # Aba 3: Memória
        self.setup_memoria_tab()
        
        # Aba 4: Log de Execução
        self.setup_log_tab()
        
        # Aba 5: Estatísticas Extras
        self.setup_estatisticas_tab()
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Pronto", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_pipeline_tab(self):
        # Aba Pipeline
        pipeline_frame = ttk.Frame(self.notebook)
        self.notebook.add(pipeline_frame, text="Pipeline")
        
        # Título
        ttk.Label(pipeline_frame, text="Estado do Pipeline RISC-V", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Frame para os estágios
        stages_frame = ttk.Frame(pipeline_frame)
        stages_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Criar widgets para cada estágio
        self.stage_widgets = {}
        stages = [
            ("IF", "Instruction Fetch"),
            ("ID", "Instruction Decode"),
            ("EX", "Execute"),
            ("MEM", "Memory Access"),
            ("WB", "Write Back")
        ]
        
        for i, (stage, description) in enumerate(stages):
            stage_frame = ttk.LabelFrame(stages_frame, text=f"{stage} - {description}", padding=10)
            stage_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
            # Frame interno para organizar conteúdo e instrução assembly
            content_frame = ttk.Frame(stage_frame)
            content_frame.pack(fill=tk.BOTH, expand=True)
            
            # Widget de texto para mostrar a instrução (lado esquerdo)
            text_widget = tk.Text(content_frame, height=4, width=35, wrap=tk.WORD, state=tk.DISABLED)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Label para instrução assembly (lado direito)
            assembly_frame = ttk.Frame(content_frame)
            assembly_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
            
            ttk.Label(assembly_frame, text="Instrução:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
            assembly_label = tk.Label(assembly_frame, text="", font=("Courier", 10), 
                                    justify=tk.LEFT, anchor=tk.W, wraplength=200,
                                    relief=tk.SUNKEN, bg="lightgray", padx=5, pady=5)
            assembly_label.pack(fill=tk.BOTH, expand=True)
            
            self.stage_widgets[stage] = {'text': text_widget, 'assembly': assembly_label}
            
    def setup_registradores_tab(self):
        # Aba Registradores
        reg_frame = ttk.Frame(self.notebook)
        self.notebook.add(reg_frame, text="Registradores")
        
        # Título
        ttk.Label(reg_frame, text="Banco de Registradores", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Frame com scroll
        canvas = tk.Canvas(reg_frame)
        scrollbar = ttk.Scrollbar(reg_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Grid de registradores
        self.reg_labels = {}
        for i in range(32):
            row = i // 4
            col = i % 4
            
            # Nome do registrador
            reg_name = f"x{i}"
            if i == 0: reg_name += " (zero)"
            elif i == 1: reg_name += " (ra)"
            elif i == 2: reg_name += " (sp)"
            
            frame = ttk.Frame(scrollable_frame)
            frame.grid(row=row, column=col, padx=10, pady=5, sticky="w")
            
            ttk.Label(frame, text=f"{reg_name}:", width=12).pack(side=tk.LEFT)
            
            value_label = ttk.Label(frame, text="0", font=("Courier", 10), width=10, relief=tk.SUNKEN)
            value_label.pack(side=tk.LEFT)
            
            self.reg_labels[i] = value_label
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def setup_memoria_tab(self):
        # Aba Memória
        mem_frame = ttk.Frame(self.notebook)
        self.notebook.add(mem_frame, text="Memória")
        
        # Título
        ttk.Label(mem_frame, text="Conteúdo da Memória", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Frame para controles de memória
        mem_control_frame = ttk.Frame(mem_frame)
        mem_control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(mem_control_frame, text="Mostrar endereços:").pack(side=tk.LEFT)
        
        # Text widget para memória
        self.memoria_text = scrolledtext.ScrolledText(mem_frame, height=20, font=("Courier", 10))
        self.memoria_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def setup_log_tab(self):
        # Aba Log
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="Log de Execução")
        
        # Título
        ttk.Label(log_frame, text="Log de Execução Detalhado", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Frame para controles do log
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(log_control_frame, text="Limpar Log", command=self.limpar_log).pack(side=tk.LEFT)
        ttk.Button(log_control_frame, text="Salvar Log", command=self.salvar_log).pack(side=tk.LEFT, padx=10)
        
        # Text widget para log
        self.log_text = scrolledtext.ScrolledText(log_frame, height=25, font=("Courier", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def setup_estatisticas_tab(self):
        # Aba Estatísticas das Funcionalidades Extras
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="Estatísticas Extras")
        
        # Título
        ttk.Label(stats_frame, text="Estatísticas das Funcionalidades Extras", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # Frame principal para as estatísticas
        main_stats_frame = ttk.Frame(stats_frame)
        main_stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Frame para previsão de desvio
        pred_frame = ttk.LabelFrame(main_stats_frame, text="Previsão de Desvio de 2 bits", padding=10)
        pred_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Labels para estatísticas de previsão
        self.lbl_pred_status = ttk.Label(pred_frame, text="Status: DESABILITADA", font=("Arial", 10, "bold"))
        self.lbl_pred_status.pack(anchor=tk.W)
        
        self.lbl_pred_corretos = ttk.Label(pred_frame, text="Previsões corretas: 0")
        self.lbl_pred_corretos.pack(anchor=tk.W)
        
        self.lbl_pred_incorretos = ttk.Label(pred_frame, text="Previsões incorretas: 0")
        self.lbl_pred_incorretos.pack(anchor=tk.W)
        
        self.lbl_pred_taxa = ttk.Label(pred_frame, text="Taxa de acerto: 0.0%")
        self.lbl_pred_taxa.pack(anchor=tk.W)
        
        # Frame para forwarding
        fwd_frame = ttk.LabelFrame(main_stats_frame, text="Forwarding", padding=10)
        fwd_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.lbl_fwd_status = ttk.Label(fwd_frame, text="Status: DESABILITADO", font=("Arial", 10, "bold"))
        self.lbl_fwd_status.pack(anchor=tk.W)
        
        self.lbl_fwd_realizados = ttk.Label(fwd_frame, text="Forwards realizados: 0")
        self.lbl_fwd_realizados.pack(anchor=tk.W)
        
        # Frame para detecção de hazards
        haz_frame = ttk.LabelFrame(main_stats_frame, text="Detecção de Hazards", padding=10)
        haz_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.lbl_haz_status = ttk.Label(haz_frame, text="Status: DESABILITADA", font=("Arial", 10, "bold"))
        self.lbl_haz_status.pack(anchor=tk.W)
        
        self.lbl_haz_stalls = ttk.Label(haz_frame, text="Stalls por hazard: 0")
        self.lbl_haz_stalls.pack(anchor=tk.W)
        
        # Frame para tabela de previsão
        table_frame = ttk.LabelFrame(main_stats_frame, text="Tabela de Previsão de Desvios", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # TreeView para tabela de previsão
        columns = ('PC', 'Estado', 'Descrição')
        self.pred_table = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        # Configurar colunas
        self.pred_table.heading('PC', text='PC (Hex)')
        self.pred_table.heading('Estado', text='Estado')
        self.pred_table.heading('Descrição', text='Descrição')
        
        self.pred_table.column('PC', width=120)
        self.pred_table.column('Estado', width=80)
        self.pred_table.column('Descrição', width=200)
        
        # Scrollbar para tabela
        table_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.pred_table.yview)
        self.pred_table.configure(yscrollcommand=table_scroll.set)
        
        self.pred_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        table_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def atualizar_configuracoes(self):
        """Atualiza as configurações das funcionalidades extras no simulador"""
        if self.simulador:
            self.simulador.previsao_desvio_habilitada = self.var_previsao_desvio.get()
            self.simulador.forwarding_habilitado = self.var_forwarding.get()
            self.simulador.deteccao_hazards_habilitada = self.var_deteccao_hazards.get()
            
            # Reset estatísticas
            self.simulador.desvios_corretos = 0
            self.simulador.desvios_incorretos = 0
            self.simulador.stalls_por_hazard = 0
            self.simulador.forwards_realizados = 0
            
            self.log(f"Configurações atualizadas: Previsão={self.var_previsao_desvio.get()}, "
                    f"Forwarding={self.var_forwarding.get()}, Hazards={self.var_deteccao_hazards.get()}")
    
    def abrir_arquivo(self):
        arquivo = filedialog.askopenfilename(
            title="Selecionar arquivo Assembly ou binário",
            filetypes=[("Assembly files", "*.asm"), ("All files", "*.*")]
        )
        
        if arquivo:
            if arquivo.endswith('.asm'):
                self.arquivo_asm = arquivo
            elif arquivo.endswith('.bin'):
                self.arquivo_bin = arquivo

            self.lbl_arquivo.config(text=os.path.basename(arquivo), foreground="black")
            self.status_bar.config(text=f"Arquivo carregado: {os.path.basename(arquivo)}")
            
            # Montar o arquivo
            try:
                if self.arquivo_asm:
                    base_name = arquivo.rsplit('.', 1)[0]
                    self.montador.montar(arquivo, base_name)
                    
                    # Inicializar simulador com opções extras
                    data_file = f"{base_name}_data.bin"
                    text_file = f"{base_name}_text.bin"
                    
                    opcoes_extras = {
                        'previsao_desvio': self.var_previsao_desvio.get(),
                        'forwarding': self.var_forwarding.get(),
                        'deteccao_hazards': self.var_deteccao_hazards.get()
                    }
                    
                    self.simulador = Simulador(data_file, text_file, opcoes_extras)
                    self.wb_buffer = {}  # Inicializar buffer do WB

                elif self.arquivo_bin:
                    base_name = os.path.basename(arquivo)
                    self.simulador = Simulador(None, base_name)
                    
                # Habilitar botões
                self.btn_executar.config(state=tk.NORMAL)
                self.btn_executar_tudo.config(state=tk.NORMAL)
                self.btn_reset.config(state=tk.NORMAL)
                
                # Atualizar displays
                self.atualizar_interface()
                
                # Preparar arquivo de saída
                if self.arquivo_asm:
                    self.arquivo_saida = "saida.out"
                else:
                    self.arquivo_saida = "saida.out"
                with open(self.arquivo_saida, 'w', encoding='utf-8') as f:
                    f.write("=== LOG DE EXECUÇÃO DO SIMULADOR RISC-V ===\n\n")
                
                self.log("Arquivo montado e simulador inicializado com sucesso!")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao processar arquivo: {str(e)}")
                
    def executar_ciclo(self):
        """Executa um ciclo do simulador"""
        if not self.simulador:
            return
            
        try:
            # Capturar o que estava em MEM_WB antes da execução (isso irá para WB)
            self.wb_buffer = self.simulador.MEM_WB.copy() if self.simulador.MEM_WB else {}
            
            # Executar um ciclo
            self.simulador.executar_ciclo()
            
            # Atualizar interface
            self.atualizar_interface()
            
            # Log do ciclo
            self.log_ciclo()
            
            # Verificar se terminou
            if self.simulador_terminou():
                self.btn_executar.config(state=tk.DISABLED)
                self.btn_executar_tudo.config(state=tk.DISABLED)
                self.status_bar.config(text="Execução finalizada")
                self.log("=== EXECUÇÃO FINALIZADA ===")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro durante execução: {str(e)}")
            
    def executar_tudo(self):
        """Executa o programa completo"""
        if not self.simulador:
            return
            
        self.executando = True
        self.btn_executar_tudo.config(state=tk.DISABLED)
        
        try:
            ciclo_inicial = self.simulador.ciclo
            while not self.simulador_terminou() and self.simulador.ciclo < 10000:
                self.executar_ciclo()
                
                # Atualizar interface a cada 10 ciclos para melhor performance
                if self.simulador.ciclo % 10 == 0:
                    self.root.update()
                    
            self.log(f"Execução completa em {self.simulador.ciclo - ciclo_inicial} ciclos")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro durante execução: {str(e)}")
        finally:
            self.executando = False
            
    def reset_simulador(self):
        """Reseta o simulador para o estado inicial"""
        if self.arquivo_asm:
            try:
                base_name = self.arquivo_asm.rsplit('.', 1)[0]
                data_file = f"{base_name}_data.bin"
                text_file = f"{base_name}_text.bin"
                
                self.simulador = Simulador(data_file, text_file)
                self.wb_buffer = {}  # Limpar o buffer do WB
                self.atualizar_interface()
                
                self.btn_executar.config(state=tk.NORMAL)
                self.btn_executar_tudo.config(state=tk.NORMAL)
                
                self.status_bar.config(text="Simulador resetado")
                self.log("=== SIMULADOR RESETADO ===")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao resetar: {str(e)}")
                
    def simulador_terminou(self):
        """Verifica se o simulador terminou a execução"""
        if not self.simulador:
            return True
            
        return (self.simulador.pc >= len(self.simulador.instrucoes) * 4 and
                not self.simulador.IF_ID and
                not self.simulador.ID_EX and
                not self.simulador.EX_MEM and
                not self.simulador.MEM_WB)
    
    def capturar_estado_pipeline(self):
        """Captura o estado atual do pipeline"""
        if not self.simulador:
            return {}
            
        # Antes de executar o ciclo, salvar o que estava em MEM_WB como o atual WB
        self.wb_buffer = self.simulador.MEM_WB.copy() if self.simulador.MEM_WB else {}
            
        return {
            'IF_ID': self.simulador.IF_ID.copy(),
            'ID_EX': self.simulador.ID_EX.copy(),
            'EX_MEM': self.simulador.EX_MEM.copy(),
            'MEM_WB': self.simulador.MEM_WB.copy(),
            'WB': self.wb_buffer.copy(),
            'pc': self.simulador.pc,
            'ciclo': self.simulador.ciclo
        }
        
    def atualizar_interface(self):
        """Atualiza toda a interface com o estado atual"""
        if not self.simulador:
            return
            
        # Atualizar ciclo
        self.lbl_ciclo.config(text=str(self.simulador.ciclo))
        
        # Atualizar pipeline
        self.atualizar_pipeline()
        
        # Atualizar registradores
        self.atualizar_registradores()
        
        # Atualizar memória
        self.atualizar_memoria()
        
        # Atualizar estatísticas das funcionalidades extras
        self.atualizar_estatisticas_extras()
        
    def atualizar_pipeline(self):
        """Atualiza a visualização do pipeline"""
        if not self.simulador:
            return
            
        # Mapear estágios para seus dados
        stage_data = {
            'IF': self.simulador.IF_ID,
            'ID': self.simulador.ID_EX,
            'EX': self.simulador.EX_MEM,
            'MEM': self.simulador.MEM_WB,
            'WB': self.wb_buffer  # Usar o buffer para mostrar o que está sendo processado no WB
        }
        
        for stage, data in stage_data.items():
            widgets = self.stage_widgets[stage]
            text_widget = widgets['text']
            assembly_label = widgets['assembly']
            
            # Atualizar widget de texto
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            
            # Atualizar instrução assembly
            assembly_text = ""
            
            if stage == 'IF' and data:
                instrucao_hex = f"0x{data['instrucao']:08X}"
                pc_hex = f"0x{data['pc']:08X}"
                text_widget.insert(tk.END, f"PC: {pc_hex}\nInstrução: {instrucao_hex}\n")
                text_widget.insert(tk.END, f"Binário: {data['instrucao']:032b}")
                # Para IF, precisamos decodificar a instrução para mostrar o assembly
                assembly_text = self.decodificar_instrucao_raw(data['instrucao'])
                
            elif stage == 'ID' and data:
                text_widget.insert(tk.END, f"Tipo: {data.get('tipo', 'N/A')}\n")
                if 'rd' in data:
                    text_widget.insert(tk.END, f"RD: x{data['rd']}\n")
                if 'rs1' in data:
                    text_widget.insert(tk.END, f"RS1: x{data['rs1']}\n")
                if 'rs2' in data:
                    text_widget.insert(tk.END, f"RS2: x{data['rs2']}\n")
                if 'imm' in data:
                    text_widget.insert(tk.END, f"IMM: {data['imm']}")
                assembly_text = self.simulador.instrucao_para_assembly(data)
                    
            elif stage == 'EX' and data:
                text_widget.insert(tk.END, f"Tipo: {data.get('tipo', 'N/A')}\n")
                if 'resultado' in data:
                    text_widget.insert(tk.END, f"Resultado: {data['resultado']}\n")
                if 'endereco' in data:
                    text_widget.insert(tk.END, f"Endereço: 0x{data['endereco']:08X}\n")
                if 'desvia' in data:
                    text_widget.insert(tk.END, f"Desvia: {data['desvia']}\n")
                assembly_text = self.simulador.instrucao_para_assembly(data)
                    
            elif stage == 'MEM' and data:
                text_widget.insert(tk.END, f"Tipo: {data.get('tipo', 'N/A')}\n")
                if 'resultado' in data:
                    text_widget.insert(tk.END, f"Dados: {data['resultado']}\n")
                assembly_text = self.simulador.instrucao_para_assembly(data)
                    
            elif stage == 'WB' and data:
                text_widget.insert(tk.END, f"Tipo: {data.get('tipo', 'N/A')}\n")
                if 'rd' in data and data.get('rd', 0) != 0:
                    text_widget.insert(tk.END, f"Escrevendo em x{data['rd']}\n")
                if 'resultado' in data:
                    text_widget.insert(tk.END, f"Valor: {data['resultado']}\n")
                else:
                    text_widget.insert(tk.END, "Nenhuma escrita\n(instrução tipo S/B)")
                assembly_text = self.simulador.instrucao_para_assembly(data)
                
            if not data:
                if stage == 'WB':
                    text_widget.insert(tk.END, "Nenhuma operação\nde write-back")
                else:
                    text_widget.insert(tk.END, "Nenhuma instrução\nno estágio")
                assembly_text = ""
                
            text_widget.config(state=tk.DISABLED)
            
            # Atualizar label da instrução assembly
            assembly_label.config(text=assembly_text if assembly_text else "---")
            
    def decodificar_instrucao_raw(self, instr):
        """Decodifica uma instrução raw para formato assembly (para estágio IF)"""
        opcode = instr & 0x7F
        
        if opcode == 0b0110011:  # Tipo R
            rd = (instr >> 7) & 0x1F
            funct3 = (instr >> 12) & 0x7
            rs1 = (instr >> 15) & 0x1F
            rs2 = (instr >> 20) & 0x1F
            funct7 = (instr >> 25) & 0x7F
            
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
                
        elif opcode == 0b0010011:  # Tipo I
            rd = (instr >> 7) & 0x1F
            funct3 = (instr >> 12) & 0x7
            rs1 = (instr >> 15) & 0x1F
            imm = (instr >> 20) & 0xFFF
            imm = imm - 4096 if imm & 0x800 else imm
            
            if funct3 == 0:
                return f"ADDI x{rd}, x{rs1}, {imm}"
            else:
                return f"I-type x{rd}, x{rs1}, {imm}"
                
        elif opcode == 0b0000011:  # LW
            rd = (instr >> 7) & 0x1F
            rs1 = (instr >> 15) & 0x1F
            imm = (instr >> 20) & 0xFFF
            imm = imm - 4096 if imm & 0x800 else imm
            return f"LW x{rd}, {imm}(x{rs1})"
            
        elif opcode == 0b0100011:  # SW
            rs1 = (instr >> 15) & 0x1F
            rs2 = (instr >> 20) & 0x1F
            imm11_5 = (instr >> 25) & 0x7F
            imm4_0 = (instr >> 7) & 0x1F
            imm = (imm11_5 << 5) | imm4_0
            imm = imm - 4096 if imm & 0x800 else imm
            return f"SW x{rs2}, {imm}(x{rs1})"
            
        elif opcode == 0b1100011:  # Tipo B
            funct3 = (instr >> 12) & 0x7
            rs1 = (instr >> 15) & 0x1F
            rs2 = (instr >> 20) & 0x1F
            imm12 = (instr >> 31) & 0x1
            imm10_5 = (instr >> 25) & 0x3F
            imm4_1 = (instr >> 8) & 0xF
            imm11 = (instr >> 7) & 0x1
            imm = (imm12 << 12) | (imm11 << 11) | (imm10_5 << 5) | (imm4_1 << 1)
            imm = imm - 8192 if imm & 0x1000 else imm
            
            if funct3 == 0:
                return f"BEQ x{rs1}, x{rs2}, {imm}"
            elif funct3 == 1:
                return f"BNE x{rs1}, x{rs2}, {imm}"
            else:
                return f"B-type x{rs1}, x{rs2}, {imm}"
                
        elif opcode == 0b1101111:  # JAL
            rd = (instr >> 7) & 0x1F
            imm = (
                ((instr >> 31) & 0x1) << 20 |
                ((instr >> 21) & 0x3FF) << 1 |
                ((instr >> 20) & 0x1) << 11 |
                ((instr >> 12) & 0xFF) << 12
            )
            imm = imm - (1 << 21) if imm & (1 << 20) else imm
            return f"JAL x{rd}, {imm}"
            
        return "Instrução desconhecida"
            
    def atualizar_registradores(self):
        """Atualiza a visualização dos registradores"""
        if not self.simulador:
            return
            
        for i in range(32):
            valor = self.simulador.bancoReg[i]
            self.reg_labels[i].config(text=f"{valor}")
            
            # Destacar registradores modificados (simplificado)
            if valor != 0 and i != 0:  # x0 sempre é 0
                self.reg_labels[i].config(background="lightblue")
            else:
                self.reg_labels[i].config(background="white")
                
    def atualizar_memoria(self):
        """Atualiza a visualização da memória"""
        if not self.simulador:
            return
            
        self.memoria_text.delete(1.0, tk.END)
    
        # Mostrar apenas posições preenchidas
        self.memoria_text.insert(tk.END, "Endereços de memória com dados:\n\n")
        enderecos_ordenados = sorted(self.simulador.memoria_dados.keys())
        
        for endereco in enderecos_ordenados:
            valor = self.simulador.memoria_dados[endereco]
            self.memoria_text.insert(tk.END, f"0x{endereco:08X}: 0x{valor:08X} ({valor})\n")
                
        if not self.simulador.memoria_dados:
            self.memoria_text.insert(tk.END, "Nenhum dado na memória")
            
    def atualizar_estatisticas_extras(self):
        """Atualiza as estatísticas das funcionalidades extras"""
        if not self.simulador:
            return
            
        stats = self.simulador.obter_estatisticas()
        
        # Previsão de desvio
        pred_stats = stats['previsao_desvio']
        status_pred = "HABILITADA" if pred_stats['habilitada'] else "DESABILITADA"
        self.lbl_pred_status.config(text=f"Status: {status_pred}")
        self.lbl_pred_corretos.config(text=f"Previsões corretas: {pred_stats['desvios_corretos']}")
        self.lbl_pred_incorretos.config(text=f"Previsões incorretas: {pred_stats['desvios_incorretos']}")
        self.lbl_pred_taxa.config(text=f"Taxa de acerto: {pred_stats['taxa_acerto']:.1f}%")
        
        # Forwarding
        fwd_stats = stats['forwarding']
        status_fwd = "HABILITADO" if fwd_stats['habilitado'] else "DESABILITADO"
        self.lbl_fwd_status.config(text=f"Status: {status_fwd}")
        self.lbl_fwd_realizados.config(text=f"Forwards realizados: {fwd_stats['forwards_realizados']}")
        
        # Detecção de hazards
        haz_stats = stats['hazards']
        status_haz = "HABILITADA" if haz_stats['deteccao_habilitada'] else "DESABILITADA"
        self.lbl_haz_status.config(text=f"Status: {status_haz}")
        self.lbl_haz_stalls.config(text=f"Stalls por hazard: {haz_stats['stalls_por_hazard']}")
        
        # Atualizar tabela de previsão
        self.atualizar_tabela_previsao()
        
    def atualizar_tabela_previsao(self):
        """Atualiza a tabela de previsão de desvios"""
        if not self.simulador:
            return
            
        # Limpar tabela
        for item in self.pred_table.get_children():
            self.pred_table.delete(item)
            
        # Adicionar entradas da tabela de previsão
        if hasattr(self.simulador, 'tabela_previsao'):
            for pc, estado in self.simulador.tabela_previsao.items():
                descricoes = {
                    0: "Strongly Not Taken",
                    1: "Weakly Not Taken", 
                    2: "Weakly Taken",
                    3: "Strongly Taken"
                }
                
                descricao = descricoes.get(estado, "Desconhecido")
                self.pred_table.insert('', 'end', values=(f"0x{pc:08X}", estado, descricao))
            
    def log_ciclo(self):
        """Registra informações do ciclo atual no log e arquivo"""
        if not self.simulador:
            return
            
        ciclo = self.simulador.ciclo
        
        # Log na interface
        log_msg = f"\n=== CICLO {ciclo} ===\n"
        
        # Pipeline
        log_msg += "Pipeline:\n"
        log_msg += f"  IF: {self.formato_instrucao_pipeline('IF')}\n"
        log_msg += f"  ID: {self.formato_instrucao_pipeline('ID')}\n"
        log_msg += f"  EX: {self.formato_instrucao_pipeline('EX')}\n"
        log_msg += f"  MEM: {self.formato_instrucao_pipeline('MEM')}\n"
        log_msg += f"  WB: {self.formato_instrucao_pipeline('WB')}\n"
        
        # Registradores modificados
        log_msg += "\nRegistradores não-zero:\n"
        for i in range(32):
            if self.simulador.bancoReg[i] != 0:
                log_msg += f"  x{i}: {self.simulador.bancoReg[i]}\n"
                
        # Memória
        log_msg += "\nMemória:\n"
        for endereco in sorted(self.simulador.memoria_dados.keys()):
            valor = self.simulador.memoria_dados[endereco]
            log_msg += f"  0x{endereco:08X}: 0x{valor:08X}\n"
            
        # Informações das funcionalidades extras
        if hasattr(self.simulador, 'obter_estatisticas'):
            stats = self.simulador.obter_estatisticas()
            
            # Se há atividade relevante, incluir no log
            if (stats['previsao_desvio']['habilitada'] and 
                (stats['previsao_desvio']['desvios_corretos'] > 0 or stats['previsao_desvio']['desvios_incorretos'] > 0)):
                log_msg += f"\nPrevisão de Desvio: {stats['previsao_desvio']['desvios_corretos']} corretas, {stats['previsao_desvio']['desvios_incorretos']} incorretas\n"
                
            if stats['forwarding']['habilitado'] and stats['forwarding']['forwards_realizados'] > 0:
                log_msg += f"Forwards realizados: {stats['forwarding']['forwards_realizados']}\n"
                
            if stats['hazards']['deteccao_habilitada'] and stats['hazards']['stalls_por_hazard'] > 0:
                log_msg += f"Stalls por hazard: {stats['hazards']['stalls_por_hazard']}\n"
            
        self.log(log_msg)
        
        # Salvar no arquivo
        if self.arquivo_saida:
            try:
                with open(self.arquivo_saida, 'a', encoding='utf-8') as f:
                    f.write(log_msg + "\n")
            except Exception as e:
                print(f"Erro ao escrever no arquivo de saída: {e}")
                
    def formato_instrucao_pipeline(self, stage):
        """Formata a instrução para exibição no pipeline"""
        stage_data = {
            'IF': self.simulador.IF_ID,
            'ID': self.simulador.ID_EX, 
            'EX': self.simulador.EX_MEM,
            'MEM': self.simulador.MEM_WB,
            'WB': self.wb_buffer
        }
        
        data = stage_data.get(stage, {})
        
        if not data:
            return "vazio"
            
        if stage == 'IF':
            return f"0x{data.get('instrucao', 0):08X} (PC: 0x{data.get('pc', 0):08X})"
        elif stage == 'WB':
            tipo = data.get('tipo', '')
            if 'rd' in data and data.get('rd', 0) != 0:
                return f"{tipo} -> x{data['rd']}"
            else:
                return f"{tipo} (sem write-back)"
        elif 'tipo' in data:
            return f"{data['tipo']}"
        else:
            return "processando"
            
    def log(self, mensagem):
        """Adiciona mensagem ao log"""
        self.log_text.insert(tk.END, mensagem + "\n")
        self.log_text.see(tk.END)
        
    def limpar_log(self):
        """Limpa o log"""
        self.log_text.delete(1.0, tk.END)
        
    def salvar_log(self):
        """Salva o log em arquivo"""
        arquivo = filedialog.asksaveasfilename(
            title="Salvar log",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if arquivo:
            try:
                with open(arquivo, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("Sucesso", f"Log salvo em {arquivo}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar log: {str(e)}")

def main():
    root = tk.Tk()
    app = InterfaceSimuladorRISCV(root)
    root.mainloop()

if __name__ == "__main__":
    main()
