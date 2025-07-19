#!/usr/bin/env python3
"""
Script para demonstrar as funcionalidades extras do simulador RISC-V:
- Previsão de desvio de 2 bits
- Forwarding 
- Detecção de hazards de dados
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from montador import Montador
from simulador import Simulador

def teste_funcionalidades_extras():
    """Testa as funcionalidades extras com diferentes configurações"""
    
    # Montar o arquivo de teste
    montador = Montador()
    arquivo_teste = "Teste_Extras.asm"
    
    if not os.path.exists(arquivo_teste):
        print(f"Erro: Arquivo {arquivo_teste} não encontrado!")
        return
    
    print("Montando arquivo de teste...")
    montador.montar(arquivo_teste, "Teste_Extras")
    
    # Configurações para teste
    configuracoes = [
        {
            'nome': 'Simulador Básico (sem extras)',
            'opcoes': {
                'previsao_desvio': False,
                'forwarding': False,
                'deteccao_hazards': False
            }
        },
        {
            'nome': 'Com Detecção de Hazards apenas',
            'opcoes': {
                'previsao_desvio': False,
                'forwarding': False,
                'deteccao_hazards': True
            }
        },
        {
            'nome': 'Com Forwarding apenas',
            'opcoes': {
                'previsao_desvio': False,
                'forwarding': True,
                'deteccao_hazards': False
            }
        },
        {
            'nome': 'Com Forwarding + Detecção de Hazards',
            'opcoes': {
                'previsao_desvio': False,
                'forwarding': True,
                'deteccao_hazards': True
            }
        },
        {
            'nome': 'Com Previsão de Desvio apenas',
            'opcoes': {
                'previsao_desvio': True,
                'forwarding': False,
                'deteccao_hazards': False
            }
        },
        {
            'nome': 'Todas as Funcionalidades Habilitadas',
            'opcoes': {
                'previsao_desvio': True,
                'forwarding': True,
                'deteccao_hazards': True
            }
        }
    ]
    
    for config in configuracoes:
        print("\n" + "="*60)
        print(f"TESTANDO: {config['nome']}")
        print("="*60)
        
        # Criar simulador com configuração específica
        simulador = Simulador("Teste_Extras_data.bin", "Teste_Extras_text.bin", config['opcoes'])
        
        # Executar simulação
        simulador.executar(mostrar_detalhes=False)
        
        # Mostrar estatísticas
        stats = simulador.obter_estatisticas()
        
        print(f"Ciclos executados: {simulador.ciclo}")
        
        # Previsão de desvio
        pred_stats = stats['previsao_desvio']
        if pred_stats['habilitada']:
            total_desvios = pred_stats['desvios_corretos'] + pred_stats['desvios_incorretos']
            print(f"Previsão de Desvio:")
            print(f"  - Total de desvios: {total_desvios}")
            print(f"  - Corretos: {pred_stats['desvios_corretos']}")
            print(f"  - Incorretos: {pred_stats['desvios_incorretos']}")
            print(f"  - Taxa de acerto: {pred_stats['taxa_acerto']:.1f}%")
        else:
            print("Previsão de Desvio: DESABILITADA")
        
        # Forwarding
        fwd_stats = stats['forwarding']
        if fwd_stats['habilitado']:
            print(f"Forwarding: {fwd_stats['forwards_realizados']} forwards realizados")
        else:
            print("Forwarding: DESABILITADO")
        
        # Detecção de hazards
        haz_stats = stats['hazards']
        if haz_stats['deteccao_habilitada']:
            print(f"Detecção de Hazards: {haz_stats['stalls_por_hazard']} stalls inseridos")
        else:
            print("Detecção de Hazards: DESABILITADA")
        
        # Resultado final
        print(f"\nRegistradores finais (apenas não-zero):")
        for i in range(32):
            if simulador.bancoReg[i] != 0:
                print(f"  x{i}: {simulador.bancoReg[i]}")
        
        print(f"\nMemória final:")
        for endereco in sorted(simulador.memoria_dados.keys()):
            valor = simulador.memoria_dados[endereco]
            print(f"  0x{endereco:08X}: {valor}")

def main():
    print("=== DEMONSTRAÇÃO DAS FUNCIONALIDADES EXTRAS ===")
    print("Este script testa as seguintes funcionalidades:")
    print("a) Previsão de desvio de 2 bits com flush do pipeline")
    print("b) Forwarding para resolver hazards de dados")
    print("c) Detecção de hazards de dados com inserção de stalls")
    print()
    
    try:
        teste_funcionalidades_extras()
        print("\n" + "="*60)
        print("DEMONSTRAÇÃO CONCLUÍDA!")
        print("Para uma experiência interativa, execute: python interface_grafica.py")
        print("e carregue o arquivo Teste_Extras.asm")
    except Exception as e:
        print(f"Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
