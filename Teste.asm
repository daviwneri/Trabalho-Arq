.data
valor1: .word 15      # memória[0] = 15
valor2: .word 27      # memória[4] = 27
resultado: .word 0    # memória[8] = 0 

.text
    LW x1, 0(x0)         # x1 = valor1 (15)
    LW x2, 4(x0)         # x2 = valor2 (27)

    ADDI x0, x0, 0       # NOPE
    ADDI x0, x0, 0       # NOPE

    ADD x3, x1, x2       # x3 = x1 + x2 = 15 + 27 = 42

    ADDI x0, x0, 0       # NOPE
    ADDI x0, x0, 0       # NOPE

    SW x3, 8(x0)         # resultado = x3 (42)

    ADDI x4, x0, 42      # x4 = 42
    BEQ x3, x4, iguais   # se x3 == 42, desvia para "iguais"

    ADDI x5, x0, 0       # será pulado se BEQ for verdadeiro

iguais:
    ADDI x6, x0, 1       # x6 = 1 (indicador de sucesso)

    JAL x0, fim          # pula para "fim"

    ADDI x7, x0, 15       # será pulado

fim:
    ADDI x10, x0, 99     # x10 = 99