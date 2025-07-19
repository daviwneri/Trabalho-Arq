.data
valor1: .word 10   
valor2: .word 20   
valor3: .word 30
resultado1: .word 0
resultado2: .word 0    

.text
    # Teste de hazards de dados e forwarding
    LW x1, 0(x0)      # Load valor1 (10)
    ADDI x2, x1, 5    # Hazard RAW: x1 ainda não está disponível (x2 = 15)
    
    LW x3, 4(x0)      # Load valor2 (20)  
    ADD x4, x1, x3    # Possível forwarding de x1 e x3
    
    # Teste de previsão de desvio
    ADDI x5, x0, 3    # x5 = 3 (contador)
    
loop:
    ADDI x6, x6, 1    # x6++ 
    ADDI x5, x5, -1   # x5-- (decrementa contador)
    BNE x5, x0, loop  # Desvio condicional (será tomado 3 vezes)
    
    # Mais testes de hazards
    LW x7, 8(x0)      # Load valor3 (30)
    ADD x8, x7, x4    # Hazard: x7 do LW anterior
    SUB x9, x8, x1    # Possível forwarding de x8
    
    # Armazenar resultados
    SW x4, 12(x0)     # Salvar resultado1
    SW x9, 16(x0)     # Salvar resultado2
    
    # Desvio incondicional
    JAL x10, fim
    
    # Esta instrução não deve ser executada
    ADDI x11, x0, 999
    
fim:
    ADDI x12, x0, 100  # x12 = 100 (fim do programa)
