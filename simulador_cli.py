#!/usr/bin/env python3
"""
Simulador RISC-V com Pipeline - Linha de Comando
Suporta funcionalidades extras configuráveis via argumentos
"""

import argparse
import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from montador import Montador
from simulador import Simulador

def main():
    parser = argparse.ArgumentParser(description='Simulador RISC-V com Pipeline e Funcionalidades Extras')
    
    # Argumentos obrigatórios
    parser.add_argument('arquivo', help='Arquivo assembly (.asm) para simular')
    
    # Funcionalidades extras (opcionais)
    parser.add_argument('--previsao-desvio', action='store_true',
                       help='Habilitar previsão de desvio de 2 bits')
    parser.add_argument('--forwarding', action='store_true',
                       help='Habilitar forwarding (bypass)')
    parser.add_argument('--deteccao-hazards', action='store_true',
                       help='Habilitar detecção de hazards de dados')
    
    # Opções de execução
    parser.add_argument('--detalhado', action='store_true',
                       help='Mostrar detalhes de cada ciclo')
    parser.add_argument('--estatisticas', action='store_true',
                       help='Mostrar apenas estatísticas finais')
    parser.add_argument('--output', '-o', type=str,
                       help='Arquivo de saída para log detalhado')
    
    args = parser.parse_args()
    
    # Verificar se arquivo existe
    if not os.path.exists(args.arquivo):
        print(f"Erro: Arquivo '{args.arquivo}' não encontrado!")
        return 1
    
    # Configurar opções extras
    opcoes_extras = {
        'previsao_desvio': args.previsao_desvio,
        'forwarding': args.forwarding,
        'deteccao_hazards': args.deteccao_hazards
    }
    
    print("=== SIMULADOR RISC-V COM PIPELINE ===")
    print(f"Arquivo: {args.arquivo}")
    print("Funcionalidades habilitadas:")
    print(f"  - Previsão de Desvio: {'SIM' if args.previsao_desvio else 'NÃO'}")
    print(f"  - Forwarding: {'SIM' if args.forwarding else 'NÃO'}")
    print(f"  - Detecção de Hazards: {'SIM' if args.deteccao_hazards else 'NÃO'}")
    print()
    
    try:
        # Montar arquivo
        print("Montando arquivo...")
        montador = Montador()
        base_name = args.arquivo.rsplit('.', 1)[0]
        montador.montar(args.arquivo, base_name)
        
        # Criar simulador
        data_file = f"{base_name}_data.bin"
        text_file = f"{base_name}_text.bin"
        simulador = Simulador(data_file, text_file, opcoes_extras)
        
        # Configurar saída
        if args.output:
            # Redirecionar saída para arquivo se especificado
            original_stdout = sys.stdout
            with open(args.output, 'w', encoding='utf-8') as f:
                sys.stdout = f
                simulador.executar(mostrar_detalhes=args.detalhado)
            sys.stdout = original_stdout
            print(f"Log detalhado salvo em: {args.output}")
        else:
            # Executar normalmente
            mostrar_detalhes = args.detalhado and not args.estatisticas
            simulador.executar(mostrar_detalhes=mostrar_detalhes)
        
        # Mostrar estatísticas
        if args.estatisticas or not args.detalhado:
            print("\n" + "="*50)
            print("RESULTADO DA SIMULAÇÃO")
            print("="*50)
            
            stats = simulador.obter_estatisticas()
            
            print(f"Ciclos executados: {simulador.ciclo}")
            print()
            
            # Registradores finais
            print("Registradores finais (apenas não-zero):")
            registradores_nao_zero = False
            for i in range(32):
                if simulador.bancoReg[i] != 0:
                    print(f"  x{i}: {simulador.bancoReg[i]}")
                    registradores_nao_zero = True
            if not registradores_nao_zero:
                print("  (todos os registradores são zero)")
            print()
            
            # Memória final
            print("Memória final:")
            if simulador.memoria_dados:
                for endereco in sorted(simulador.memoria_dados.keys()):
                    valor = simulador.memoria_dados[endereco]
                    print(f"  0x{endereco:08X}: {valor}")
            else:
                print("  (memória vazia)")
            print()
            
            # Estatísticas das funcionalidades extras
            print("ESTATÍSTICAS DAS FUNCIONALIDADES EXTRAS:")
            
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
            
            print("="*50)
        
        return 0
        
    except Exception as e:
        print(f"Erro durante a execução: {e}")
        if args.detalhado:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
