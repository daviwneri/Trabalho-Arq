.data
valor1: .word 15   
valor2: .word 27   
resultado: .word 0    

.text
    LW x1, 0(x0)
    LW x2, 4(x0)

    ADDI x0, x0, 0
    ADDI x0, x0, 0

    ADD x3, x1, x2

    ADDI x0, x0, 0
    ADDI x0, x0, 0

    SW x3, 8(x0)

    ADDI x4, x0, 42 
    BEQ x3, x4, iguais

    ADDI x5, x0, 0

iguais:
    ADDI x6, x0, 1

    JAL x0, fim 

    ADDI x7, x0, 15 

fim:
    ADDI x10, x0, 99 