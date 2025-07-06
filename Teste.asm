.data
    array: .word 10, 20, 30, 40
    size:  .word 4
    result: .word 0

.text
main:
    addi x5, zero, 0       
    addi x6, zero, 0       
    lw   x7, 0(size)       
    
    addi x8, zero, array   

loop:
    bge  x5, x7, end_loop  
    
    slli x9, x5, 2         
    add  x9, x8, x9        
    lw   x10, 0(x9)        
    
    add  x6, x6, x10
    
    addi x5, x5, 1
    j    loop

end_loop:
    sw   x6, 0(result)     
    
    jal  x0, fim

fim:
    j fim                  
