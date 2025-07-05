.data
    array: .word 10, 20, 30, 40
    size:  .word 4
    result: .word 0

.text
main:
    # Inicialização
    addi x5, zero, 0       # i = 0
    addi x6, zero, 0       # sum = 0
    lw   x7, 0(size)       # x7 = size
    
    # Carrega endereço do array
    addi x8, zero, array   # x8 = &array[0]

loop:
    bge  x5, x7, end_loop  # if i >= size, termina
    
    # Calcula endereço do elemento
    slli x9, x5, 2         # i * 4 (offset)
    add  x9, x8, x9        # x9 = &array[i]
    lw   x10, 0(x9)        # x10 = array[i]
    
    # Soma ao total
    add  x6, x6, x10
    
    # Incrementa i
    addi x5, x5, 1
    j    loop

end_loop:
    # Armazena resultado
    sw   x6, 0(result)     # result = sum
    
    # Termina o programa
    jal  x0, fim

fim:
    j fim                  # Loop infinito