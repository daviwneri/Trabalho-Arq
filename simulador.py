# Memória principal
memPrinc = []

# Banco de registradores
bancReg = []
bancReg[0] = 0

dicRegist = {
    "zero": 0,
    "ra": 1,
    "sp": 2,
    "gp": 3,     
    "tp": 4, 
    "t0": 5,  
    "t1": 6,  
    "t2": 7,  
    "s0": 8, 
    "s1": 9,    
    "a0": 10,
    "a1": 11,  
    "a2": 12,
    "a3": 13, 
    "a4": 14,  
    "a5": 15,
    "a6": 16,  
    "a7": 17,  
    "s2": 18,  
    "s3": 19,  
    "s4": 20,  
    "s5": 21, 
    "s6": 22, 
    "s7": 23, 
    "s8": 24, 
    "s9": 25,  
    "s10": 26,
    "s11": 27,  
    "t3": 28, 
    "t4": 29,  
    "t5": 30, 
    "t6": 31 
}


# Acesso a ULA (etapa 3)
def acesso_ula (regd, reg1, x, op):
    if (op is None):
        print("Operação não encontrada")
        return None

    elif (op == 'soma'):
        regd = reg1 + x

    elif (op == 'sub'):
        regd = reg1 - x

    elif (op == 'mult'):
        regd = reg1*x

    else:
        print("Operação inválida")
        return None
    
    return regd


# Acesso a memória de dados (etapa 4)
def acesso_mem_dados (dest, orig, op):
    if (op is None):
        print("Operação não encontrada")
        return None
    
    elif (op == 'sw'):
        memPrinc[dest] = orig
    
    elif (op == 'lw'):
        conteudo = memPrinc[orig]
        return conteudo

    else:
        print("Operação inválida")
        return None
    

# Escrita no banco de registradores (etapa 5)
def ecrita_banc_reg (regd, x):
    bancReg[regd] = x

