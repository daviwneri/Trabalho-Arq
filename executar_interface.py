#!/usr/bin/env python3
"""
Script para testar a interface gráfica do simulador RISC-V
"""

import sys
import os

# Adicionar o diretório atual ao path para importar os módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from interface_grafica import main
    print("Iniciando interface gráfica do simulador RISC-V...")
    main()
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    print("Certifique-se de que todos os arquivos estão no mesmo diretório:")
    print("- interface_grafica.py")
    print("- montador.py") 
    print("- simulador.py")
    print("- Teste.asm")
except Exception as e:
    print(f"Erro ao executar a interface: {e}")
    import traceback
    traceback.print_exc()
