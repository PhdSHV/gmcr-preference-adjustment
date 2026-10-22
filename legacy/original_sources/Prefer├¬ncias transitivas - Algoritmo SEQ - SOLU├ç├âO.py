from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus
import math
# Conjuntos
S = set(range(12))  # Conjunto de estados
N = set(range(2))									# Conjunto de decisores
s = 10 # Estado focal

# Dados (Exemplo: substitua com leitura de arquivo externo)
# J[n][a][b]: n in N, a in S, b in S
# P[n][a][b]: n in N, a in S, b in S
#J = [[[0 for _ in S] for _ in S] for _ in N]  # Preencher com dados reais
#P = [[[0 for _ in S] for _ in S] for _ in N]  # Preencher com dados reais

#Ler os arquivos J1 escolhido:

J1 = []							# cria uma lista vazia

dados = open('J1-12est.csv', 'r').readlines() #puxa dados de arquivo externo, na mesma pasta desse arquivo

for x in dados: 
    J1texto = x.split(',') 		# criando variavel tipo lista que recebe cada palavra da frase como uma entrada da lista
                                        # mudando o separador para ,

    J1int = []						# cria uma lista vazia

    for k in J1texto:					# laço para pegar cada parte da lista criadae muda para o tipo INT e coloca na lista, 
        J1int.append(int(k))			# antes vazia, 

    J1.append(J1int)
    
#Ler os arquivos J2 escolhido:

J2 = []							# cria uma lista vazia

dados = open('J2-12est.csv', 'r').readlines() #puxa dados de arquivo externo, na mesma pasta desse arquivo

for x in dados: 
    J2texto = x.split(',') 		# criando variavel tipo lista que recebe cada palavra da frase como uma entrada da lista
                                        # mudando o separador para ,

    J2int = []						# cria uma lista vazia

    for k in J2texto:					# laço para pegar cada parte da lista criadae muda para o tipo INT e coloca na lista, 
        J2int.append(int(k))			# antes vazia, 

    J2.append(J2int)
    J=[J1,J2]
#Ler os arquivos P1 escolhido:

P1 = []							# cria uma lista vazia

dados = open('P1-12est.csv', 'r').readlines() #puxa dados de arquivo externo, na mesma pasta desse arquivo

for x in dados: 
    P1texto = x.split(',') 		# criando variavel tipo lista que recebe cada palavra da frase como uma entrada da lista
                                        # mudando o separador para ,

    P1int = []						# cria uma lista vazia

    for k in P1texto:					# laço para pegar cada parte da lista criadae muda para o tipo INT e coloca na lista, 
        P1int.append(int(k))			# antes vazia, 

    P1.append(P1int)
#Ler os arquivos P2 escolhido:

P2 = []							# cria uma lista vazia

dados = open('P2-12est.csv', 'r').readlines() #puxa dados de arquivo externo, na mesma pasta desse arquivo

for x in dados: 
    P2texto = x.split(',') 		# criando variavel tipo lista que recebe cada palavra da frase como uma entrada da lista
                                        # mudando o separador para ,

    P2int = []						# cria uma lista vazia

    for k in P2texto:					# laço para pegar cada parte da lista criadae muda para o tipo INT e coloca na lista, 
        P2int.append(int(k))			# antes vazia, 

    P2.append(P2int)

P = [P1,P2]

# Modelo
model = LpProblem("Optimization_Model", LpMinimize)

# Variáveis de decisão
X = [[[LpVariable(f"X_{i}_{a}_{b}",0,1, cat="Binary") for b in S] for a in S] for i in N]
Y = [[LpVariable(f"Y_{i}_{a}",0,1, cat="Binary") for a in S] for i in N]
Z = [[[LpVariable(f"Z_{i}_{a}_{b}",0,1, cat="Binary") for b in S] for a in S] for i in N]
V = [[[[LpVariable(f"V_{i}_{a}_{b}_{k}",0,1, cat="Binary")   for k in S] for b in S] for a in S] for i in N]


# A variável V[i][a][b] = 1 significa que o estado b não é menos preferível que o estado s
# e nem é preferível que o estado a para o decisor i, ou seja, b "está entre" a e s e, caso a preferência
# entre os estados a e s for alterada, a preferênciaentra b e s deve ser alterada por transitividade.



#model += lpSum(
#    X[i][s][a]
#    + lpSum(V[i, s, k] * (1 + P[i][s][k] * P[i][k][a]) for k in S if k != a)
#    for i in N
#    for a in S
#    if P[i][s][a] == 1
#)




# Função objetivo
objective = 0
for i in N:
    for a in S:
            if P[i][s][a] ==1:
                # Parte correspondente a X[i][s][a]
                term1 = X[i][s][a]
               # Parte correspondente a V[i, s, k] * (1 + P[i][s][k] * P[i][k][a]) para k em S, k != a
                term2 = 0
                for k in S:
                    if k != a and k!= s and (P[i][a][k] + P[i][k][s] == 0 or P[i][s][k] + P[i][k][a] == 0):
                        term2 += V[i][s][a][k] * (1 + P[i][k][a] * P[i][s][k] + P[i][k][s]*P[i][a][k])
                term3 = 0
                term4 = 0
                for b in S:
                    term3 += X[1-i][a][b]*(1+P[1-i][b][a])
                    for k in S:
                        if k != b and k!= a  and (P[1-i][b][k] + P[1-i][k][a] == 0 or P[1-i][a][k] + P[1-i][k][b] == 0):
                            term4 += V[1-i][a][b][k]*(1 + P[1-i][k][b]*P[1-i][a][k] + P[1-i][k][a]*P[1-i][b][k])
                # Soma ao objetivo
                objective += term1 + term2 + term3 + term4

# Adicionar a função objetivo ao modelo
model += objective

#==================== Restrições  =======================

#==================== Restrição 1 =======================  ok Restrição 1 do pdf


                  
for i in N:
    for a in S:
            if J[i][s][a] * P[i][s][a] ==1:
                # Parte correspondente a X[i][s][a]
                term1 = X[i][s][a] + Y[i][a]
                # Parte correspondente a V[i, s, k] * (1 + P[i][s][k] * P[i][k][a]) para k em S, k != a
                term2 = 0
                for k in S:
                    if k != a and k!= s and P[i][k][a] + P[i][a][s] == 0:
                        term2 += V[i][s][k][a] 
                
                # Soma ao objetivo
                model += term1 + term2 >=1








#for i in N:
#    for a in S:
#        if J[i][s][a] == 1 and P[i][s][a] * math.prod(P[i][s][b] for b in S if J[1 - i][a][b] == 1) == 1 :
#                contIntermed = 0
#                for k in S:
#                        if P[i][k][a] + P[i][a][s] == 0 and k!= a and k!=s:
#                            model += X[i][s][a] + V[i][s][k][a] + Y[i][a] >= 1
#                            contIntermed += 1
#                if contIntermed == 0:            
#                    model +=  X[i][s][a] + Y[i][a] >=1
            
#==================== Restrição 2 =======================  Acho que ok
for i in N:
    for a in S:
        if J[i][s][a]*P[i][s][a] == 1:
            term1 = 0
            cont = 0
            for b in S:
                if  math.prod(P[i][s][b] for b in S if P[1-i][a][b]*J[1 - i][a][b] == 1) >= 1 and  J[1 - i][a][b] == 1 and b!=a:
                    term1 += Z[i][a][b]
                if J[1 - i][a][b] == 0:
                    cont += 1
            if term1 !=0 or cont == len(S):
                model+=  term1- Y[i][a] >= 0                          
            

    
#==================== Restrição 3 =======================  acho que ok
for i in N:
    for a in S:        
        if P[i][s][a]*J[i][s][a] == 1:
            for b in S:
                term1 = 0
                if P[i][s][b]*J[1-i][a][b] == 1:
                    for k in S:
                        if k != b and k!= s and  P[i][k][b] + P[i][b][s] == 0:
                            term1 += V[i][s][k][b]
                    model+=  term1 + X[i][s][b] - Z[i][a][b] >= 0
                    
                    

#==================== Restrição 4 =======================            



for i in N:
    for a in S:        
        if P[i][s][a]*J[i][s][a] == 1:
            for b in S:
                if J[1-i][a][b]*(1-P[1-i][a][b]) == 1:
                    term1 = 0
                    for k in S:
                        if k != b and k!= a  and P[1-i][k][b] + P[1-i][b][a] == 0:
                            term1 += V[1-i][a][k][b]
                    model+=  term1 + X[1-i][a][b] - Z[i][a][b] >= 0
                    

#==================== Restrição 5 =======================
                    
for i in N:
    for a in S:
        for b in S:
            if a< b:
                model += X[1-i][a][b] + X[1-i][b][a] - 1 <=0




#==================== Restrição 6 =======================

for i in N:
    for a in S:
        if a != s :
            for k in S:
                if k != a and k !=s and (P[i][a][k] + P[i][k][s] == 0 or P[i][s][k] + P[i][k][a] == 0) :
                    model +=   X[i][s][a]- V[i][s][a][k]   == 0

            
#==================== Restrição 7 =======================

for i in N:
    for a in S:
        for b in S:
            for k in S:
                if k != a and k !=b and (P[1-i][b][k] + P[1-i][k][a]== 0 or P[1-i][a][k]+ P[1-i][k][b]== 0) :
                    model +=   X[1-i][a][b]- V[1-i][a][b][k]   == 0            
    
          



# Resolvendo o modelo
model.solve()

# Abrindo um arquivo para salvar o relatório completo
with open("resultado_completo_SEQ.txt", "w") as f:
    # Título do relatório
    f.write("Relatório de Resultados - Modelo de Programação Linear\n")
    f.write("="*50 + "\n")

    # Escrever a formulação do modelo de forma controlada
    f.write("Formulação do Modelo:\n")
    f.write("Função Objetivo: " + str(model.objective) + "\n")
    
    f.write("\nRestrições:\n")
    for name, constraint in model.constraints.items():
        f.write(f"{name}: {constraint}\n")

    # Escrever os resultados
    f.write("\nResultados:\n")
    f.write(f"Status: {LpStatus[model.status]}\n")
    
    # Exibir apenas variáveis com valor diferente de zero
    f.write("\nVariáveis com valor diferente de zero:\n")
    for v in model.variables():
        if v.varValue is not None and v.varValue != 0:
            f.write(f"{v.name} = {v.varValue}\n")
    
    # Escrever a função objetivo
    f.write(f"\nValor da Função Objetivo: {model.objective.value()}\n")

    # Finalização
    f.write("="*50 + "\n")
    f.write("Relatório Finalizado.")
