from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus
import math
# Conjuntos
S = set(range(12))  # Conjunto de estados
N = set(range(2))	# Conjunto de decisores
s = 10										# Estado focal

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
                    if k != a and k!= s and P[i][a][k] + P[i][k][s] == 0:
                        term2 += V[i][s][a][k] * (1 + P[i][k][a] * P[i][s][k])
                
                # Soma ao objetivo
                objective += term1 + term2

# Adicionar a função objetivo ao modelo
model += objective

#==================== Restrições  =======================

#==================== Restrição 1 =======================  ok Restrição 1 do pdf


                  
for i in N:
    for a in S:
            if J[i][s][a]*P[i][s][a] == 1:
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
            term2 = 0
            cont=0
            for b in S:
                if  math.prod(P[i][s][b] for b in S if J[1 - i][a][b] == 1)== 1 and J[1 - i][a][b] == 1 and b!=a:
                    term1 += X[i][s][b]
                    for k in S:
                        if k != b and k!= s and  P[i][k][b] + P[i][b][s] == 0:
                            term2 += V[i][s][k][b]
                if J[1 - i][a][b] == 0:
                    cont += 1
            if ((term1 != 0 and term2 !=0) or (cont == len(S))):                
                model+= term1 + term2 - Y[i][a] >= 0                        
            
            

    
            

#==================== Restrição 3 =======================            
#for i in N:
#    for a in S:       
#       if J[i][s][a] == 1 and P[i][s][a] * math.prod(P[i][s][b] for b in S if J[1 - i][a][b] == 1) == 1:
#            model += Y[i][a] >= 0
#            model += Y[i][a] <= 1
#V = [[0 for a in S] for i in N]

for i in N:
    for a in S:
        if a != s:
            for k in S:
                if k != a and k !=s and P[i][a][k] + P[i][k][s] == 0:
                    model +=   X[i][s][a]- V[i][s][a][k]   == 0




#==================== Restrição 4 =======================
#for i in N:
#    for a in S:
#        if a != s:
#            for k in S:
#                 if k != a and k !=s and P[i][s][a] == 1 and P[i][a][k] + P[i][k][s] == 0:
#                     model +=   -X[i][s][a]+ V[i][s][k][a]   <= 0





U = [[[0 for b in S] for a in S] for i in N]
W = [[[0 for b in S] for a in S] for i in N]
for i in N:
    for a in S:
        if a != s:
            for k in S:
                if k != a and k !=s and P[i][s][a] == 1 and P[i][a][k] + P[i][k][s] == 0:
                    U[i][a][k] = 1
#                   W[i][a][b] += U[i][a][k] * (1 + P[i][k][b] * P[i][a][k])    
    

            
            
K = [[sum(P[i][a][s] for a in S) for s in S] for i in N]           

#==================== Restrição 5 =======================                

#for i in N:
#    for a in S:
#        for b in S:
#            for k in S:
#                if P[i][k][s] + P[i][a][k] == 0 and k!= a and k != s:
#                    model += X[i][s][a] - V[i][a] >= 0
#                else:
#                    model += X[i][s][a] == W[i][s][a]  

# Resolvendo o modelo
model.solve()

# Abrindo um arquivo para salvar o relatório completo
with open("resultado_completo_GMR.txt", "w") as f:
    # Título do relatório
    f.write("Relatório de Resultados - Modelo de Programação Linear - Equilíbrio GMR\n")
    f.write("="*50 + "\n")
    # ==================================================
    # EXIBINDO AS PREFERÊNCIAS ORIGINAIS 
    # ==================================================
    f.write("\n" + "="*50 + "\n")
    f.write("PREFERÊNCIAS ORIGINAIS (P_i):\n")
    f.write("="*50 + "\n")

    for i in range(len(K)):
        # Cria lista de pares (estado, valor K)
        estados_K = [(s_idx, K[i][s_idx]) for s_idx in range(len(K[i]))]

        # Ordena do maior para o menor valor de K
        estados_K.sort(key=lambda x: x[1], reverse=True)

        # Agrupa estados com mesmo valor de K
        grupos = []
        grupo_atual = [str(estados_K[0][0])]
        valor_atual = estados_K[0][1]

        for s_idx, valor in estados_K[1:]:
            if valor == valor_atual:
                grupo_atual.append(str(s_idx))  # Mesmo valor -> empate
            else:
                grupos.append(grupo_atual)
                grupo_atual = [str(s_idx)]
                valor_atual = valor
        grupos.append(grupo_atual)

        # Monta a string de preferência
        partes = []
        for g in grupos:
            if len(g) == 1:
                partes.append(g[0])  # apenas um estado
            else:
                partes.append("~".join(g))  # estados empatados

        relacao_preferencia = " > ".join(partes)

        # Escreve no relatório
        
        f.write(f"P_{i}: {relacao_preferencia}\n")

    # ==================================================
    # CONSTRUINDO E EXIBINDO AS NOVAS PREFERÊNCIAS (P'_i)
    # ==================================================
    f.write("\n" + "="*50 + "\n")
    f.write("NOVAS PREFERÊNCIAS (P'_i) APÓS A OTIMIZAÇÃO:\n")
    f.write("="*50 + "\n")

    # Inicializar W com cópia dos valores de K
    W_novo = [[K[i][a] for a in range(len(S))] for i in range(len(N))]
    
    # Atualizar W conforme os valores de X obtidos no modelo
    for v in model.variables():
        if v.name.startswith("V_") and v.varValue is not None:
            parts = v.name.split("_")  # ['X', 'i', 'a', 'b']
            i = int(parts[1])
            a = int(parts[2])
            b = int(parts[3])
            c = int(parts[4])
            v_val = round(v.varValue)

            if v_val == 1:
                # Se X[i][a][b] = 1, então W[i][b] recebe K[i][a]
                W_novo[i][c] = K[i][c]-1
            
    for v in model.variables():
        if v.name.startswith("X_") and v.varValue is not None:
            parts = v.name.split("_")  # ['X', 'i', 'a', 'b']
            i = int(parts[1])
            a = int(parts[2])
            b = int(parts[3])
            x_val = round(v.varValue)

            if x_val == 1:
                # Se X[i][a][b] = 1, então W[i][b] recebe K[i][a]
                W_novo[i][b] = K[i][b] - 1
                W_novo[i][a] =  W_novo[i][b]
            #else:
                # Se X[i][a][b] = 0, mantém o valor original
             #   W_novo[i][a] = K[i][a]
    
    
                
    for i in N:
        for a in S:
            f.write(f"W[{i}][{a}] = {W_novo[i][a]}          K[{i}][{a}] = {K[i][a]} \n")
    
    f.write("\n" + "="*50 + "\n")                
    # Exibir as novas preferências P'_i
    for i in range(len(W_novo)):
        # Cria lista de pares (estado, valor W)
        estados_W = [(s_idx, W_novo[i][s_idx]) for s_idx in range(len(W_novo[i]))]

        # Ordena do maior para o menor valor
        estados_W.sort(key=lambda x: x[1], reverse=True)

        # Agrupa empates
        grupos = []
        grupo_atual = [str(estados_W[0][0])]
        valor_atual = estados_W[0][1]

        for s_idx, valor in estados_W[1:]:
            if valor == valor_atual:
                grupo_atual.append(str(s_idx))  # mesmo valor -> indiferença
            else:
                grupos.append(grupo_atual)
                grupo_atual = [str(s_idx)]
                valor_atual = valor
        grupos.append(grupo_atual)

        # Montar string de preferência com ≻ e ~
        partes = []
        for g in grupos:
            if len(g) == 1:
                partes.append(g[0])
            else:
                partes.append(" ~ ".join(g))
        relacao_preferencia = " > ".join(partes)

        # Escrever no relatório
        
        f.write(f"P'_{i}: {relacao_preferencia}\n")
    # Escrever a formulação do modelo de forma controlada
    f.write("\n" + "="*50 + "\n")
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
    
    f.write("\n" + "="*50 + "\n")
    
    # Escrever a função objetivo
    f.write(f"\nValor da Função Objetivo: {model.objective.value()}\n")

    # Finalização
    f.write("="*50 + "\n")
    f.write("Relatório Finalizado.")
    print(cont)
