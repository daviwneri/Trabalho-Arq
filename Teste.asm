.data
valor: .word 20

.text
    ADDI x1, x0, 10      # x1 = 10
    ADDI x2, x0, 20      # x2 = 20
    ADD x3, x1, x2       # x3 = x1 + x2 = 30
    SW x3, 0(x0)         # Mem[0] = x3
    LW x4, 0(x0)         # x4 = Mem[0] = 30
    BEQ x3, x4, fim      # Salta para fim se iguais
    ADDI x5, x0, 99      # (pulado se BEQ for tomado)
fim:
    ADDI x6, x0, 123     # x6 = 123