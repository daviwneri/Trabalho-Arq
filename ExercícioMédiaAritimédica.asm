.data
inputNum: .asciz "Insira a quantidade de notas a serem registradas: "
inputNota: .asciz "Insira uma nota: "
resultado: .asciz "A média é: "

.text

start:
li a7, 4
la a0, inputNum
ecall

li a7, 5
ecall
mv t0, a0

mv t1, zero
mv s0, zero


loop:
bge t1, t0, end

li a7, 4
la a0, inputNota
ecall

li a7, 5
ecall
mv t2, a0

add s0, s0, t2
addi t1, t1, 1

j loop


end:
fcvt.s.w f1, s0
fcvt.s.w f2, t0

fdiv.s f3, f1, f2

li a7, 4
la a0, resultado
ecall

fmv.s fa0, f3
li a7, 2
ecall

li a7, 10
ecall

