from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus, value, PULP_CBC_CMD, CPLEX_CMD
import math
import numpy
# Conjuntos
# Definição dos parâmetros

horizonte_h = 6 # Horizonte de movimento limitado
S = set(range(5))  # Conjunto de estados
N = set(range(2))	# Conjunto de decisores
s = 2										# Estado focal



#Ler os arquivos J1 escolhido:

J1 = []							# cria uma lista vazia

dados = open('J1-5est.csv', 'r').readlines() #puxa dados de arquivo externo, na mesma pasta desse arquivo

for x in dados: 
    J1texto = x.split(',') 		# criando variavel tipo lista que recebe cada palavra da frase como uma entrada da lista
                                        # mudando o separador para ,

    J1int = []						# cria uma lista vazia

    for k in J1texto:					# laço para pegar cada parte da lista criadae muda para o tipo INT e coloca na lista, 
        J1int.append(int(k))			# antes vazia, 

    J1.append(J1int)
    
#Ler os arquivos J2 escolhido:

J2 = []							# cria uma lista vazia

dados = open('J2-5est.csv', 'r').readlines() #puxa dados de arquivo externo, na mesma pasta desse arquivo

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

dados = open('P1-5est.csv', 'r').readlines() #puxa dados de arquivo externo, na mesma pasta desse arquivo

for x in dados: 
    P1texto = x.split(',') 		# criando variavel tipo lista que recebe cada palavra da frase como uma entrada da lista
                                        # mudando o separador para ,

    P1int = []						# cria uma lista vazia

    for k in P1texto:					# laço para pegar cada parte da lista criadae muda para o tipo INT e coloca na lista, 
        P1int.append(int(k))			# antes vazia, 

    P1.append(P1int)
#Ler os arquivos P2 escolhido:

P2 = []							# cria uma lista vazia

dados = open('P2-5est.csv', 'r').readlines() #puxa dados de arquivo externo, na mesma pasta desse arquivo

for x in dados: 
    P2texto = x.split(',') 		# criando variavel tipo lista que recebe cada palavra da frase como uma entrada da lista
                                        # mudando o separador para ,

    P2int = []						# cria uma lista vazia

    for k in P2texto:					# laço para pegar cada parte da lista criadae muda para o tipo INT e coloca na lista, 
        P2int.append(int(k))			# antes vazia, 

    P2.append(P2int)

P = [P1,P2]
M= len(S)
########## Modelo############
model = LpProblem("Optimization_Model", LpMinimize)

# Variáveis de decisão
C = [[[LpVariable(f"C_{i}_{a}_{b}",0,1, cat="Binary") for b in S] for a in S] for i in N]
D = [[[[LpVariable(f"D_{i}_{j}_{a}_{h}", 0, 1, cat="Binary") for h in range(0,horizonte_h+1)]  for a in S] for j in N] for i in N]
Da =[[[[[LpVariable(f"Da_{i}_{j}_{a}_{b}_{h}", 0, 1, cat="Binary") for h in range(0,horizonte_h+1)]  for b in S] for a in S]  for j in N] for i in N]
W = [[LpVariable(f"W_{i}_{a}", lowBound=0, upBound=M, cat="Integer") for a in S] for i in N]
A = [[[[LpVariable(f"A_{i}_{j}_{a}_{h}", cat="Integer") for h in range(0,horizonte_h +1)] for a in S] for j in N] for i in N]
t = [[[LpVariable(f"t_{i}_{a}_{b}", 0,1,cat="Binary") for b in S] for a in S] for i in N]
X1 = [[[LpVariable(f"X1_{i}_{a}_{b}", 0,1,cat="Binary") for b in S] for a in S] for i in N]
Z3 = [[[[LpVariable(f"Z3_{i}_{a}_{b}_{h}", cat="Binary") for h in range(0,horizonte_h +1)] for b in S] for a in S] for i in N]


# Calcular K para todos os estados e decisores
K = [[sum(P[i][a][s] for a in S) for s in S] for i in N]









# Função objetivo
objective = lpSum(C[i][a][b] for i in N for a in S for b in S if a !=b )

model += objective
#==================== Restrições  =======================

#==================== Restrição 1 =======================

for i in N:
    for a in S:
        for b in S:
            if a != b: #adicionada essa condição para evitar C[i][a][a]
                model += C[i][a][b]*M*M >= (W[i][a] - W[i][b]) * (K[i][b] - K[i][a])
       
#==================== Restrições 2 e 3 =======================     

for i in N:
    for a in S:
        for b in S:
            if a != b:
                model += W[i][b] >= W[i][a] + 1 - M * (1 - X1[i][a][b])
                model += W[i][b] <= W[i][a] + M * X1[i][a][b]

#==================== Restrições adicionada 23/04/2026 =======================
for i in N:
    for a in S:
        for b in S:
            if a < b:
                model += X1[i][a][b] + X1[i][b][a] == 1
                
            elif a==b:
                model += X1[i][a][b] == 0
                
                
#==================== Restrições 4 a 7 =======================                 
                
for i in N:
    for a in S:
        for h in range(1,horizonte_h + 1):
            model += A[i][i][a][h] >= W[i][a]
            model += A[i][i][a][h] <= W[i][a] +  M* (1 - D[i][i][a][h])
            model += A[i][1-i][a][h] <= W[i][a]
            model += A[i][1-i][a][h] >= W[i][a] - M * (1 - D[i][1-i][a][h])


#==================== Restrições 8 a 11 ======================= 
for i in N:
    j = 1 - i

    for a in S:
        for b in S:
            for h in range(1, horizonte_h + 1):

                # lado focal credível
                if J[i][a][b] == 1:
                    model += A[i][i][a][h] >= \
                             A[i][j][b][h-1] - M * (1 - X1[i][a][b])

                    model += A[i][i][a][h] <= \
                             A[i][j][b][h-1] + \
                             M * (2 - Da[i][i][a][b][h] - X1[i][a][b])

                # lado oponente
                if J[j][a][b] == 1:
                    model += A[i][j][a][h] <= A[i][i][b][h-1]
                    model += A[i][j][a][h] >= \
                             A[i][i][b][h-1] - M * (1 - Da[i][j][a][b][h])
                    
                    

#==================== Restrição 12 e 13 =======================
                    
for i in N:
    j = 1 - i
    for a in S:
        for h in range(1, horizonte_h + 1):
            model += D[i][j][a][h] + \
                     lpSum(Da[i][j][a][b][h]
                           for b in S if J[j][a][b] == 1) == 1                   

            model += D[i][i][a][h] + \
                             lpSum(Z3[i][a][b][h]
                                   for b in S if J[i][a][b] == 1) == 1
            
            
#==================== Restrições 14 a 16 =================
            
            
for i in N:
    for a in S:
        for b in S:
            for h in range(1, horizonte_h + 1):
                if J[i][a][b]==1:
                    model += Z3[i][a][b][h] <= Da[i][i][a][b][h]
                    model += Z3[i][a][b][h] <= X1[i][a][b]
                    model += Z3[i][a][b][h] >= Da[i][i][a][b][h] + X1[i][a][b] - 1



    
    
#==================== Restrições 17 a 19 =================
for i in N:
    j = 1 - i

    model += A[i][i][s][horizonte_h] == W[i][s]

    for a in S:
        model += A[i][i][a][0] == W[i][a]
        model += A[i][j][a][0] == W[i][a]

#==================== Restrições 20 a 2 =================
for i in N:
    for a in S:
        model += lpSum(t[i][a][b] for b in S) == 1
        model += lpSum(b * t[i][a][b] for b in S) == W[i][a]

for i in N:
    for b in S:
        model += lpSum(t[i][a][b] for a in S) == 1





# Restrição 13
#for i in N:
#    for a in S:
#        for b in range(len(S)):
#           if W[i][a] == b:
#                model +=  t[i][a][b] ==1 
#            elif W[i][a] != b :
#                model += t[i][a][b] == 0


#==================== Restrição 9 ======================= 
#for i in N:
#    for a in S:
#        for b in S:
#            if J[i][a][b] == 1:
#                model += C[i, a, b] <= 1
            
            
            

  

# Resolvendo o modelo
model.solve(CPLEX_CMD(msg=True))

#model.solve()

print("Status =", LpStatus[model.status])

model.writeLP("modelo_maxcred_debug.lp")

# Abrindo um arquivo para salvar o relatório completo
with open("resultado_completo - Maxmim Focal Credível.txt", "w") as f:
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
   # Exibir apenas as variáveis C_ com valor diferente de zero
    f.write("\n" + "="*60 + "\n")
    f.write("VARIÁVEIS C_ COM VALOR DIFERENTE DE ZERO:\n")
    f.write("="*60 + "\n")

    for v in model.variables():
        if v.name.startswith("C_") and v.varValue not in (0, None):
            valor = int(v.varValue) if v.varValue in (0.0, 1.0) else v.varValue
            f.write(f"{v.name} = {valor}\n")

    # Exibir separadamente as variáveis sem valor (None)
    f.write("\n" + "="*60 + "\n")
    f.write("VARIÁVEIS SEM VALOR ATRIBUÍDO (None):\n")
    f.write("="*60 + "\n")

    for v in model.variables():
        if v.varValue is None:
            f.write(f"{v.name} = None\n")

    
  
        # MATRIZES DAS VARIÁVEIS Da E D (agrupadas por i, h e j)

    f.write("\n" + "="*60 + "\n")
    f.write("MATRIZES DAS VARIÁVEIS Da E D (POR i, h E j):\n")
    f.write("="*60 + "\n")

    Da_values = {}
    D_values = {}

    # ======== Armazenar valores Da[i][j][a][b][h] ========
    for v in model.variables():
        if v.name.startswith("Da_") and v.varValue is not None:
            parts = v.name.split("_")  # Exemplo: ['Da', '0', '1', '4', '7', '2']
            i = int(parts[1])
            j = int(parts[2])
            a = int(parts[3])
            b = int(parts[4])
            h = int(parts[5])
            valor = int(round(v.varValue))

            Da_values.setdefault(i, {}).setdefault(h, {}).setdefault(j, {}).setdefault(a, {})[b] = valor

    # ======== Armazenar valores D[i][j][a][h] ========
    for v in model.variables():
        if v.name.startswith("D_") and v.varValue is not None:
            parts = v.name.split("_")  # Exemplo: ['D', '0', '1', '4', '2']
            i = int(parts[1])
            j = int(parts[2])
            a = int(parts[3])
            h = int(parts[4])
            valor = int(round(v.varValue))

            D_values.setdefault(i, {}).setdefault(h, {}).setdefault(j, {})[a] = valor

    # ======== Impressão formatada ========
    for i in sorted(Da_values.keys()):
        f.write(f"\n{'-'*60}\nVARIÁVEIS D[i][j][a][h] e Da[i][j][a][b][h] PARA O DECISOR i = {i}\n{'-'*60}\n")

        for h in sorted(Da_values[i].keys()):
            f.write(f"\n--- Horizonte h = {h} ---\n")

            for j in sorted(Da_values[i][h].keys()):
                f.write(f"\n>>> DECISOR j = {j}\n")
                f.write(f"\nMatriz Da_{i}_{j}_a_b_{h} (linhas = a, colunas = b):\n")

                # Determinar os estados (a e b)
                estados_a = list(S) #alterado dia 15/10/2025
                estados_b = list(S)
                
                #estados_a = sorted(Da_values[i][h][j].keys()) #versão anterior à do dia 15/10/2025
                #estados_b = sorted({b for a in estados_a for b in Da_values[i][h][j][a].keys()})

                # Cabeçalho
                f.write("      " + " ".join(f"b={b:2}" for b in estados_b) + "\n")
                f.write("-" * (8 + len(estados_b) * 5) + "\n")

                # Linhas (estados a)  #alterado dia 15/10/2025
                for a in estados_a:
                    linha = f"a={a:2} | " + " ".join(f"{Da_values[i][h][j].get(a, {}).get(b, 0):2d}" for b in estados_b)
                    f.write(linha + "\n")

                
                #for a in estados_a:  #versão anterior à do dia 15/10/2025
                #    linha = f"a={a:2} | " + " ".join(f"{Da_values[i][h][j][a].get(b, 0):2d}" for b in estados_b)
                #    f.write(linha + "\n")

                # Exibir D[i][j][a][h]
                if i in D_values and h in D_values[i] and j in D_values[i][h]:
                    f.write(f"\nValores de D_{i}_{j}_a_{h} (por estado a):\n")
                    for a in sorted(D_values[i][h][j].keys()):
                        f.write(f"  D_{i}_{j}_{a}_{h} = {D_values[i][h][j][a]}\n")
                else:
                    f.write("\nNenhum valor de D encontrado para este i, j e h.\n")


    # ===================================================================
    # VETORES DAS VARIÁVEIS A[i][j][a][h] (AGRUPADOS POR DECISOR i, HORIZONTE h E DECISOR j)
    # ===================================================================

    f.write("\n" + "="*60 + "\n")
    f.write("VETORES DAS VARIÁVEIS A (POR DECISOR i, HORIZONTE h E DECISOR j):\n")
    f.write("="*60 + "\n")

    # Dicionário para armazenar valores
    A_values = {}

    # ======== Armazenar valores A[i][j][a][h] ========
    for v in model.variables():
        if v.name.startswith("A_") and v.varValue is not None:
            parts = v.name.split("_")  # Exemplo: ['A', '0', '1', '5', '2']
            i = int(parts[1])
            j = int(parts[2])
            a = int(parts[3])
            h = int(parts[4])
            valor = int(round(v.varValue))

            # Criação das chaves de forma segura
            if i not in A_values:
                A_values[i] = {}
            if h not in A_values[i]:
                A_values[i][h] = {}
            if j not in A_values[i][h]:
                A_values[i][h][j] = {}
            A_values[i][h][j][a] = valor

    # ======== Impressão formatada ========
    for i in sorted(A_values.keys()):
        f.write(f"\n{'-'*60}\nDECISOR i = {i}\n{'-'*60}\n")

        for h in sorted(A_values[i].keys()):
            f.write(f"\n--- Horizonte h = {h} ---\n")

            for j in sorted(A_values[i][h].keys()):
                f.write(f"\n>>> DECISOR j = {j}\n")
                f.write(f"Valores de A_{i}_{j}_a_{h} (por estado a):\n")

                for a in S:
                    valor = A_values[i][h][j].get(a, 0)
                    f.write(f"  A_{i}_{j}_{a}_{h} = {valor}\n")

                f.write("\n")  # Linha em branco entre blocos

    # Exibir os valores das variáveis W como inteiros
    f.write("\n" + "="*60 + "\n")
    f.write("VALORES DAS VARIÁVEIS W (TODOS):\n")
    f.write("="*60 + "\n")

    # Dicionário para armazenar os valores de W[i][a]
    W_values = {}

    for v in model.variables():
        if v.name.startswith("W_") and v.varValue is not None:
            parts = v.name.split("_")  # Ex: ['W', '0', '4']
            i = int(parts[1])
            a = int(parts[2])
            valor = int(round(v.varValue))  # Converte para inteiro (0, 1, 2...)
            f.write(f"{v.name} = {valor}\n")

            # Armazena o valor de W_i_a
            if i not in W_values:
                W_values[i] = {}
            W_values[i][a] = valor
    # ==================================================
    # EXIBINDO AS PREFERÊNCIAS ORIGINAIS (a partir de K)
    # ==================================================
    f.write("\n" + "="*60 + "\n")
    f.write("PREFERÊNCIAS ORIGINAIS (CONSTRUÍDAS A PARTIR DE K):\n")
    f.write("="*60 + "\n")

    # Exibir os valores de K
    for i in range(len(K)):
        f.write(f"\nVALORES DE K_{i} (TODOS):\n")
        for s_idx, valor in enumerate(K[i]):
            f.write(f"K_{i}_{s_idx} = {valor}\n")

    # Construir e exibir a preferência original P_i
    for i in range(len(K)):
        # Cria uma lista de pares (estado, valor K)
        estados_K = [(s_idx, K[i][s_idx]) for s_idx in range(len(K[i]))]

        # Ordena do maior para o menor valor de K
        estados_K.sort(key=lambda x: x[1], reverse=True)

        # Extrai apenas os índices dos estados (ordenados)
        preferencia = [str(s_idx) for s_idx, _ in estados_K]

        # Constrói a string da preferência 
        relacao_preferencia = " > ".join(preferencia)

        # Escreve no relatório
        f.write("\n" + "-"*60 + "\n")
        f.write(f"Preferência original P_{i}:  {relacao_preferencia}\n")
        f.write("-"*60 + "\n")

    # Construir e exibir as novas preferências P'_i
    f.write("\n" + "="*50 + "\n")
    f.write("NOVAS PREFERÊNCIAS GERADAS (P'_i):\n")
    f.write("="*50 + "\n")

    for i in sorted(W_values.keys()):
        # Ordena os estados (a) pelo valor de W_i_a em ordem decrescente
        sorted_states = sorted(W_values[i].items(), key=lambda x: x[1], reverse=True)
        preferencia = " > ".join(str(a) for a, _ in sorted_states)
        f.write(f"P'_{i}: {preferencia}\n")

            
    # Escrever a função objetivo
    f.write(f"\nValor da Função Objetivo: {model.objective.value()}\n")
    
    # Exibir as variáveis t em formato de matriz (0-1 inteiros)
    f.write("\n" + "="*50 + "\n")
    f.write("MATRIZES t[i][a][b] (FORMATO DE MATRIZ 0-1):\n")
    f.write("="*50 + "\n")

    # Dicionário para armazenar os valores de t agrupados por i
    t_values = {}

    # Coleta os valores de t_ do modelo
    for v in model.variables():
        if v.name.startswith("t_") and v.varValue is not None:
            parts = v.name.split("_")  # Ex: ['t', '0', '3', '2']
            i = int(parts[1])
            a = int(parts[2])
            b = int(parts[3])
            t_values.setdefault(i, {})
            t_values[i].setdefault(a, {})
            # Converte o valor para 0 ou 1 de forma segura
            t_values[i][a][b] = int(round(v.varValue))

    # Escreve cada matriz t_i no arquivo de saída
    for i in sorted(t_values.keys()):
        f.write(f"\nMatriz t_{i}:\n")
        for a in sorted(t_values[i].keys()):
            linha = [t_values[i][a].get(b, 0) for b in sorted(t_values[i][a].keys())]
            f.write(" ".join(str(val) for val in linha) + "\n")

    

    # Finalização
    f.write("="*50 + "\n")
    f.write("Relatório Finalizado.")
    




