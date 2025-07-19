# Membros do trabalho

1. Davi Wermelinger Neri Barbosa
2. João Pedro da Silveira Fontinele
3. Miguel Barros de Azevedo
4. Matheus de Lima Moura

# ⭐ FUNCIONALIDADES EXTRAS IMPLEMENTADAS ⭐

Este simulador implementa as seguintes funcionalidades extras opcionais:

## a) 🎯 Previsão de Desvio de 2 bits
- Preditor baseado em contador saturante de 2 bits por PC
- Flush do pipeline em caso de previsão incorreta
- Estados: Strongly/Weakly Not Taken, Weakly/Strongly Taken
- **Ativa/desativa via interface gráfica ou linha de comando**

## b) ⚡ Forwarding (Bypass)
- EX-EX forwarding (EX/MEM → EX)
- MEM-EX forwarding (MEM/WB → EX)
- Resolve hazards RAW sem inserir stalls
- Load-use hazards ainda causam 1 ciclo de stall (necessário)
- **Ativa/desativa via interface gráfica ou linha de comando**

## c) 🛡️ Detecção de Hazards de Dados
- Detecta hazards RAW (Read After Write)
- Insere stalls automáticos quando necessário
- Funciona em conjunto com forwarding ou independentemente
- **Ativa/desativa via interface gráfica ou linha de comando**

### Como Usar as Funcionalidades Extras:

#### Interface Gráfica:
1. Execute `python interface_grafica.py`
2. Use o menu "Configurações" ou os checkboxes na interface
3. Carregue um arquivo (ex: `Teste_Extras.asm`)
4. Observe as estatísticas na aba "Estatísticas Extras"

#### Script de Demonstração:
```bash
python demonstrar_extras.py
```

#### Programaticamente:
```python
opcoes_extras = {
    'previsao_desvio': True,
    'forwarding': True,
    'deteccao_hazards': True
}
simulador = Simulador(data_file, text_file, opcoes_extras)
```

📖 **Ver `README_EXTRAS.md` para documentação completa das funcionalidades extras.**



# Como Executar a Interface Gráfica ------------------------------------------------------------------

## Passo a Passo

1. **Abra o terminal/prompt de comando**

2. **Abra o diretório do projeto**

3. **Execute a interface gráfica**
   
   **Opção 1 - Direto:**
   ```bash
   python interface_grafica.py
   ```
   
   **Opção 2 - Com ambiente virtual (se configurado):**
   ```bash
   .venv\Scripts\python.exe interface_grafica.py
   ```
   
   **Opção 3 - Script de execução:**
   ```bash
   python executar_interface.py
   ```

4. **Configure as funcionalidades extras (NOVO!):**
   - Use o menu "Configurações" ou os checkboxes na interface
   - Marque funcionalidades desejadas:
     - ✅ **Previsão de Desvio**: Preditor de 2 bits com flush
     - ✅ **Forwarding**: Bypass para resolver hazards RAW
     - ✅ **Detecção de Hazards**: Inserção automática de stalls

5. **Na interface que abrir:**
   - Clique em "Carregar Arquivo"
   - Selecione o arquivo `Teste.asm` (exemplo básico) ou `Teste_Extras.asm` (testa funcionalidades extras)
   - Use os botões para controlar a execução:
     - "Executar Próximo Ciclo" - executa um ciclo por vez
     - "Executar Tudo" - executa o programa completo
     - "Reset" - reinicia a execução

6. **Explore as abas:**
   - **Pipeline**: Veja o estado de cada estágio (IF, ID, EX, MEM, WB)
   - **Registradores**: Estado dos 32 registradores
   - **Memória**: Conteúdo da memória
   - **Log de Execução**: Histórico detalhado da execução
   - **Estatísticas Extras**: Métricas das funcionalidades extras (NOVO!)

## Alternativa: Linha de Comando

```bash
# Simulação básica
python simulador_cli.py Teste_Extras.asm --estatisticas

# Com todas as funcionalidades extras
python simulador_cli.py Teste_Extras.asm --previsao-desvio --forwarding --deteccao-hazards --estatisticas

# Execução detalhada
python simulador_cli.py Teste.asm --forwarding --detalhado

# Ver todas as opções
python simulador_cli.py --help
```

## Demonstração das Funcionalidades Extras

```bash
python demonstrar_extras.py
```

Este script compara automaticamente 6 configurações diferentes e mostra o impacto de cada funcionalidade.

## Resolução de Problemas

### Erro "tkinter não encontrado"
- No Windows: tkinter vem com Python por padrão
- No Linux: `sudo apt-get install python3-tk`
- No macOS: `brew install python-tk`

### Erro de import dos módulos
- Certifique-se de estar no diretório correto
- Verifique se todos os arquivos estão presentes:
  - `montador.py`
  - `simulador.py` 
  - `interface_grafica.py`
  - `Teste.asm`

### Interface não abre
- Verifique se não há erros no terminal
- Tente executar com: `python -u interface_grafica.py`

## Arquivos Gerados

Após carregar um arquivo assembly, são gerados:
- `*_data.bin` - Dados binários da seção .data
- `*_text.bin` - Instruções binárias da seção .text
- `*_saida.out` - Log completo da execução

## Exemplo de Uso

1. Execute: `python interface_grafica.py`
2. Carregue: `Teste.asm`
3. Clique em "Executar Próximo Ciclo" várias vezes
4. Observe as mudanças no pipeline e registradores
5. Verifique o log para entender a execução

A interface mostra em tempo real como as instruções fluem através do pipeline RISC-V!


# Informações adicionais sobre o projeto ------------------------------------------------------------------


# Simulador RISC-V com Pipeline - Interface Gráfica

Repositório para o trabalho de arquitetura - Simulador RISC-V com pipeline e interface gráfica.

## Descrição

Este projeto implementa um simulador completo do processador RISC-V com pipeline de 5 estágios, incluindo:

- **Montador**: Converte código assembly RISC-V para código de máquina
- **Simulador**: Executa o código com pipeline de 5 estágios (IF, ID, EX, MEM, WB)
- **Interface Gráfica**: Visualização completa do estado do processador

## Estrutura do Projeto

- `montador.py` - Montador assembly para RISC-V
- `simulador.py` - Simulador com pipeline
- `interface_grafica.py` - Interface gráfica com Tkinter
- `executar_interface.py` - Script para executar a interface
- `Teste.asm` - Arquivo de exemplo para teste
- `README.md` - Este arquivo

## Funcionalidades da Interface

### 1. Carregamento de Arquivos
- Carrega arquivos `.asm` ou  `.bin`
- Monta automaticamente o código assembly
- Inicializa o simulador

### 2. Controles de Execução
- **Executar Próximo Ciclo**: Executa um ciclo por vez
- **Executar Tudo**: Executa o programa completo
- **Reset**: Reinicia o simulador

### 3. Visualização do Pipeline
- Mostra o estado de cada estágio (IF, ID, EX, MEM, WB)
- Exibe instruções em cada estágio
- Informações detalhadas de cada etapa

### 4. Banco de Registradores
- Visualização dos 32 registradores
- Destaque para registradores modificados
- Valores em decimal

### 5. Memória
- Visualização do conteúdo da memória
- Endereços em hexadecimal
- Opção para mostrar apenas posições preenchidas

### 6. Log de Execução
- Log detalhado de cada ciclo
- Salvar/exportar logs
- Arquivo de saída automático `*_saida.out`

## Como Executar

### Método 1: Interface Gráfica (Recomendado)
```bash
python interface_grafica.py
```

### Método 2: Script de Execução
```bash
python executar_interface.py
```

### Uso da Interface:
1. Execute o programa
2. Clique em "Carregar Arquivo" ou use o menu "Arquivo > Abrir arquivo .asm"
3. Selecione um arquivo assembly (ex: `Teste.asm`)
4. Use os botões para executar:
   - "Executar Próximo Ciclo" para execução passo a passo
   - "Executar Tudo" para execução completa
5. Navegue pelas abas para ver diferentes aspectos da execução

## Instruções Suportadas

### Tipo R (Registrador-Registrador)
- `ADD rd, rs1, rs2` - Adição
- `SUB rd, rs1, rs2` - Subtração  
- `MUL rd, rs1, rs2` - Multiplicação
- `DIV rd, rs1, rs2` - Divisão
- `REM rd, rs1, rs2` - Resto da divisão
- `XOR rd, rs1, rs2` - XOR lógico
- `AND rd, rs1, rs2` - AND lógico
- `OR rd, rs1, rs2` - OR lógico
- `SLL rd, rs1, rs2` - Shift left lógico
- `SRL rd, rs1, rs2` - Shift right lógico

### Tipo I (Imediato)
- `ADDI rd, rs1, imm` - Adição com imediato
- `SLLI rd, rs1, shamt` - Shift left lógico imediato
- `SRLI rd, rs1, shamt` - Shift right lógico imediato

### Memória
- `LW rd, offset(rs1)` - Load word
- `SW rs2, offset(rs1)` - Store word

### Saltos/Desvios
- `BEQ rs1, rs2, label` - Branch if equal
- `BNE rs1, rs2, label` - Branch if not equal
- `BGE rs1, rs2, label` - Branch if greater or equal
- `BLT rs1, rs2, label` - Branch if less than
- `JAL rd, label` - Jump and link
- `JALR rd, rs1, offset` - Jump and link register

### Pseudoinstruções
- `LI rd, imm` - Load immediate (convertido para ADDI)
- `MV rd, rs` - Move (convertido para ADDI rd, rs, 0)
- `NOP` - No operation (convertido para ADDI x0, x0, 0)

## Exemplo de Arquivo Assembly

```assembly
.data
valor1: .word 15      # memória[0] = 15
valor2: .word 27      # memória[4] = 27
resultado: .word 0    # memória[8] = 0 

.text
    LW x1, 0(x0)         # x1 = valor1 (15)
    LW x2, 4(x0)         # x2 = valor2 (27)
    ADD x3, x1, x2       # x3 = x1 + x2 = 42
    SW x3, 8(x0)         # resultado = x3 (42)
    ADDI x4, x0, 42      # x4 = 42
    BEQ x3, x4, iguais   # se x3 == 42, desvia
    ADDI x5, x0, 0       # será pulado

iguais:
    ADDI x6, x0, 1       # x6 = 1
    JAL x0, fim          # pula para fim

fim:
    ADDI x10, x0, 99     # x10 = 99
```

## Arquivos de Saída

O simulador gera automaticamente:
- `*_data.bin` - Dados da seção .data em binário
- `*_text.bin` - Instruções da seção .text em binário  
- `*_saida.out` - Log completo da execução

## Requisitos

- Python 3.6+
- Tkinter (geralmente incluído com Python)
- Módulos padrão: `struct`, `re`, `os`

## Características Técnicas

- **Pipeline de 5 estágios**: IF → ID → EX → MEM → WB
- **Hazard detection**: Básica (não implementa forwarding)
- **Formato RISC-V**: 32 bits, little-endian
- **Memória**: Endereçamento por bytes, palavras de 32 bits
- **Registradores**: 32 registradores de 32 bits (x0 sempre zero)

## Observações

- O registrador x0 sempre contém o valor 0
- O programa termina quando não há mais instruções no pipeline
- A interface atualiza automaticamente o estado a cada ciclo
- Todos os valores são exibidos em decimal na interface
