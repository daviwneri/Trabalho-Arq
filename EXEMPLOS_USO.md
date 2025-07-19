# Exemplos de Uso das Funcionalidades Extras

Este documento apresenta exemplos práticos de como usar as funcionalidades extras implementadas.

## 1. Interface Gráfica

### Execução Básica
```bash
python interface_grafica.py
```

### Passos na Interface:
1. Use o menu "Configurações" ou checkboxes para habilitar funcionalidades
2. Clique em "Carregar Arquivo" e selecione `Teste_Extras.asm`
3. Execute com "Executar Próximo Ciclo" ou "Executar Tudo"
4. Observe a aba "Estatísticas Extras" para ver o impacto

## 2. Linha de Comando

### Simulação Básica (sem extras)
```bash
python simulador_cli.py Teste_Extras.asm --estatisticas
```
**Resultado:** ~36 ciclos

### Com Forwarding apenas
```bash
python simulador_cli.py Teste_Extras.asm --forwarding --estatisticas
```
**Resultado:** ~29 ciclos, 4 forwards realizados

### Com Previsão de Desvio apenas
```bash
python simulador_cli.py Teste_Extras.asm --previsao-desvio --estatisticas
```
**Resultado:** Melhoria na previsão de branches

### Com Todas as Funcionalidades
```bash
python simulador_cli.py Teste_Extras.asm --previsao-desvio --forwarding --deteccao-hazards --estatisticas
```
**Resultado:** ~29 ciclos, máxima otimização

### Execução Detalhada
```bash
python simulador_cli.py Teste_Extras.asm --forwarding --detalhado
```

### Salvar Log Detalhado
```bash
python simulador_cli.py Teste_Extras.asm --previsao-desvio --forwarding --detalhado -o log_completo.txt
```

## 3. Uso Programático

### Exemplo Básico
```python
from simulador import Simulador

# Configurar funcionalidades
opcoes = {
    'previsao_desvio': True,
    'forwarding': True,
    'deteccao_hazards': True
}

# Criar e executar simulador
sim = Simulador('data.bin', 'text.bin', opcoes)
sim.executar(mostrar_detalhes=False)

# Obter estatísticas
stats = sim.obter_estatisticas()
print(f"Ciclos: {sim.ciclo}")
print(f"Forwards: {stats['forwarding']['forwards_realizados']}")
```

### Comparação de Performance
```python
from simulador import Simulador

configuracoes = [
    {'nome': 'Sem extras', 'opcoes': {}},
    {'nome': 'Com forwarding', 'opcoes': {'forwarding': True}},
    {'nome': 'Completo', 'opcoes': {'previsao_desvio': True, 'forwarding': True, 'deteccao_hazards': True}}
]

for config in configuracoes:
    sim = Simulador('data.bin', 'text.bin', config['opcoes'])
    sim.executar(mostrar_detalhes=False)
    print(f"{config['nome']}: {sim.ciclo} ciclos")
```

## 4. Script de Demonstração

### Teste Completo
```bash
python demonstrar_extras.py
```

Este script executa o mesmo programa com 6 configurações diferentes:
1. Simulador básico (sem extras)
2. Com detecção de hazards apenas
3. Com forwarding apenas  
4. Com forwarding + detecção de hazards
5. Com previsão de desvio apenas
6. Todas as funcionalidades habilitadas

## 5. Casos de Teste Específicos

### Testando Forwarding
Crie um arquivo `teste_forwarding.asm`:
```assembly
.data
val: .word 42

.text
    LW x1, 0(x0)      # x1 = 42
    ADDI x2, x1, 10   # Hazard RAW: x2 = x1 + 10 (forwarding resolve)
    ADD x3, x2, x1    # Hazard RAW: x3 = x2 + x1 (forwarding resolve)
    SW x3, 4(x0)      # Salva resultado
```

```bash
python simulador_cli.py teste_forwarding.asm --forwarding --estatisticas
```

### Testando Previsão de Desvio
Crie um arquivo `teste_branch.asm`:
```assembly
.text
    ADDI x1, x0, 5    # Contador

loop:
    ADDI x2, x2, 1    # Incrementa
    ADDI x1, x1, -1   # Decrementa contador
    BNE x1, x0, loop  # Branch predictível (tomado 4 vezes)
    
    ADDI x3, x0, 100  # Fim
```

```bash
python simulador_cli.py teste_branch.asm --previsao-desvio --estatisticas
```

### Testando Detecção de Hazards
```bash
python simulador_cli.py Teste_Extras.asm --deteccao-hazards --estatisticas
```

## 6. Interpretação dos Resultados

### Métricas Importantes:

**Ciclos Executados:**
- Menos ciclos = melhor performance
- Forwarding é a otimização que mais reduz ciclos

**Forwards Realizados:**
- Quantos hazards RAW foram resolvidos sem stall
- Cada forward economiza pelo menos 1 ciclo

**Stalls por Hazard:**
- Quantas bolhas foram inseridas
- Idealmente 0 quando forwarding está habilitado

**Taxa de Acerto da Previsão:**
- Porcentagem de branches corretamente previstos
- >50% já é benéfico
- Depende do padrão dos branches no código

### Exemplo de Interpretação:
```
Sem extras: 36 ciclos
Com forwarding: 29 ciclos
- Economia: 7 ciclos (19% melhoria)
- 4 forwards realizados
- 0 stalls (forwarding resolveu todos os hazards)
```

## 7. Depuração e Análise

### Ver Execução Passo a Passo
```bash
python simulador_cli.py Teste_Extras.asm --forwarding --detalhado
```

### Analisar Pipeline na Interface
1. Execute `python interface_grafica.py`
2. Habilite funcionalidades desejadas
3. Use "Executar Próximo Ciclo" 
4. Observe pipeline em tempo real na aba "Pipeline"

### Verificar Tabela de Previsão
1. Na interface gráfica, vá para aba "Estatísticas Extras"
2. A tabela mostra estado de cada PC com branch
3. Estados 0-1: not taken, 2-3: taken

## 8. Troubleshooting

### Forwarding não reduz ciclos:
- Verifique se há hazards RAW no código
- Load-use hazards sempre causam 1 stall mesmo com forwarding

### Previsão de desvio com baixa taxa:
- Branches irregulares são difíceis de prever
- Preditor de 2 bits funciona melhor com padrões regulares

### Muitos stalls detectados:
- Habilite forwarding para reduzir
- Ou reorganize código para evitar hazards

Use estes exemplos para explorar e validar as funcionalidades implementadas!
