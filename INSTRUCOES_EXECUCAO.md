# Como Executar a Interface Gráfica

## Passo a Passo

1. **Abra o terminal/prompt de comando**

2. **Navegue até o diretório do projeto**

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

4. **Na interface que abrir:**
   - Clique em "Carregar Arquivo" ou use o menu "Arquivo > Abrir arquivo .asm"
   - Selecione o arquivo `Teste.asm` (ou outro arquivo assembly)
   - Use os botões para controlar a execução:
     - "Executar Próximo Ciclo" - executa um ciclo por vez
     - "Executar Tudo" - executa o programa completo
     - "Reset" - reinicia a execução

5. **Explore as abas:**
   - **Pipeline**: Veja o estado de cada estágio (IF, ID, EX, MEM, WB)
   - **Registradores**: Estado dos 32 registradores
   - **Memória**: Conteúdo da memória
   - **Log de Execução**: Histórico detalhado da execução

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
