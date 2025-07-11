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
- Carrega arquivos `.asm` 
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
