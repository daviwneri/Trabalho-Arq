# Funcionalidades Extras do Simulador RISC-V

Este documento descreve as funcionalidades extras implementadas no simulador RISC-V com pipeline.

## Funcionalidades Implementadas

### a) Previsão de Desvio de 2 bits

**Descrição:** Implementa um preditor de desvio baseado em contador saturante de 2 bits para cada instrução de branch.

**Estados do Preditor:**
- 0: Strongly Not Taken (fortemente não tomado)
- 1: Weakly Not Taken (fracamente não tomado)  
- 2: Weakly Taken (fracamente tomado)
- 3: Strongly Taken (fortemente tomado)

**Como funciona:**
- Cada PC de instrução de branch mantém um contador de 2 bits
- Previsão é "tomado" se estado >= 2, "não tomado" se estado < 2
- Contador incrementa quando desvio é tomado, decrementa quando não é tomado
- Em caso de previsão incorreta, o pipeline é limpo (flush) e o PC é corrigido

**Vantagens:**
- Reduz stalls causados por desvios condicionais
- Melhora performance especialmente em loops

### b) Forwarding (Bypass)

**Descrição:** Encaminha resultados de instruções anteriores diretamente para instruções que precisam desses dados, evitando stalls desnecessários.

**Tipos de Forwarding Implementados:**
- **EX-EX Forwarding:** Do estágio EX/MEM para EX
- **MEM-EX Forwarding:** Do estágio MEM/WB para EX

**Limitações:**
- Hazards do tipo Load-Use ainda causam 1 ciclo de stall (necessário)
- Não resolve hazards de controle

**Como funciona:**
1. Detecta quando uma instrução precisa de um registrador que está sendo escrito por instrução anterior
2. Se o dado está disponível no pipeline, faz forwarding direto
3. Caso contrário, insere stall se necessário

### c) Detecção de Hazards de Dados

**Descrição:** Detecta hazards do tipo RAW (Read After Write) e insere stalls quando necessário.

**Tipos de Hazards Detectados:**
- **RAW Hazard:** Instrução tenta ler registrador que ainda não foi escrito
- **Load-Use Hazard:** Instrução usa resultado de LW imediatamente (sempre causa stall)

**Como funciona:**
1. Verifica se registradores de origem (rs1, rs2) conflitam com registrador de destino (rd) de instruções anteriores
2. Se forwarding está habilitado, só insere stall se forwarding não resolver
3. Se forwarding está desabilitado, insere stall para todos os hazards RAW

## Como Usar

### Interface Gráfica

1. **Execute a interface:**
   ```bash
   python interface_grafica.py
   ```

2. **Configure as funcionalidades:**
   - Use o menu "Configurações" ou os checkboxes na interface
   - Marque/desmarque: "Previsão de Desvio", "Forwarding", "Detecção de Hazards"

3. **Carregue um arquivo assembly:**
   - Use "Carregar Arquivo" para carregar um .asm
   - Exemplo: `Teste_Extras.asm` (incluído)

4. **Execute e observe:**
   - Use "Executar Próximo Ciclo" para execução passo a passo
   - Observe a aba "Estatísticas Extras" para ver o impacto das funcionalidades
   - A aba "Pipeline" mostra stalls quando inseridos

### Script de Demonstração

```bash
python demonstrar_extras.py
```

Este script testa todas as combinações de funcionalidades e mostra estatísticas comparativas.

### Uso Programático

```python
from simulador import Simulador

# Configurar opções
opcoes_extras = {
    'previsao_desvio': True,
    'forwarding': True, 
    'deteccao_hazards': True
}

# Criar simulador
simulador = Simulador(data_file, text_file, opcoes_extras)

# Executar
simulador.executar()

# Obter estatísticas
stats = simulador.obter_estatisticas()
print(f"Forwards realizados: {stats['forwarding']['forwards_realizados']}")
```

## Arquivos de Exemplo

### Teste_Extras.asm
Arquivo de teste que demonstra situações onde cada funcionalidade é útil:
- Hazards RAW que podem ser resolvidos com forwarding
- Load-use hazards que sempre causam stall
- Loops que se beneficiam de previsão de desvio

## Estatísticas Disponíveis

A interface e o simulador fornecem estatísticas detalhadas:

### Previsão de Desvio
- Número de previsões corretas/incorretas  
- Taxa de acerto percentual
- Tabela de previsão mostrando estado de cada PC

### Forwarding
- Número total de forwards realizados
- Identificação de onde forwarding foi aplicado

### Detecção de Hazards
- Número de stalls inseridos
- Tipos de hazards detectados

## Impacto na Performance

### Sem Funcionalidades Extras
- Todos os hazards causam stalls
- Todos os desvios causam stalls
- Performance limitada

### Com Forwarding
- Redução significativa de stalls RAW
- Load-use hazards ainda causam 1 stall (inevitable)

### Com Previsão de Desvio
- Redução de stalls em loops e código com branches predictáveis
- Pequeno overhead em branches incorretamente previstos

### Com Todas as Funcionalidades
- Performance máxima
- Código otimizado para pipeline

## Considerações de Implementação

1. **Compatibilidade:** Todas as funcionalidades são opcionais e podem ser habilitadas/desabilitadas independentemente

2. **Ciclo Simples:** O simulador ainda executa um ciclo de cada vez, mas com otimizações internas

3. **Estado do Pipeline:** Mantém rastreamento detalhado do estado de cada estágio para implementar forwarding correto

4. **Flush de Pipeline:** Implementado para corrigir previsões incorretas de desvio

## Limitações

1. **Forwarding limitado:** Não implementa forwarding de/para memória
2. **Previsão simples:** Usa contador de 2 bits por PC (não considera histórico global)
3. **Sem especulação avançada:** Não implementa execução especulativa além da previsão de desvio

## Teste e Validação

Use os arquivos de teste fornecidos para validar o funcionamento:

```bash
# Teste completo
python demonstrar_extras.py

# Teste interativo
python interface_grafica.py
# -> Carregue Teste_Extras.asm
# -> Configure funcionalidades desejadas
# -> Execute passo a passo ou completo
```

As estatísticas mostrarão o impacto de cada funcionalidade na performance do pipeline.
