from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus, value, PULP_CBC_CMD, CPLEX_CMD
import math
import numpy
# Conjuntos
# Definição dos parâmetros

horizonte_h = 2  # Horizonte de movimento limitado
S = set(range(12))  # Conjunto de estados
N = set(range(2))	# Conjunto de decisores
s = 8										# Estado focal



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

########## Modelo############
model = LpProblem("Optimization_Model", LpMinimize)

# Variáveis de decisão
C = [[[LpVariable(f"C_{i}_{a}_{b}",0,1, cat="Binary") for b in S] for a in S] for i in N]
D = [[[LpVariable(f"D_{i}_{a}_{h}", 0, 1, cat="Binary") for h in range(0,horizonte_h + 1)]  for a in S] for i in N] 
Da =[[[[LpVariable(f"Da_{i}_{a}_{b}_{h}", 0, 1, cat="Binary") for h in range(0,horizonte_h + 1)]  for b in S] for a in S]  for i in N]
W = [[LpVariable(f"W_{i}_{a}", cat="Integer") for a in S] for i in N]
#A = [[[LpVariable(f"A_{i}_{a}_{h}", cat="Integer") for h in range(0,horizonte_h +1)] for a in S] for i in N]
t = [[[LpVariable(f"t_{i}_{a}_{b}", 0,1,cat="Binary") for b in S] for a in S] for i in N]
B = [[[[LpVariable(f"B_{i}_{a}_{b}_{h}", cat="Integer") for h in range(0,horizonte_h + 1)]  for b in S] for a in S] for i in N]
#ArgV = [[[[LpVariable(f"B_{i}_{a}_{b}_{h}", 0, 1, cat="Binary") for h in range(0,horizonte_h+1)]  for b in S] for a in S] for i in N]
V =[[[LpVariable(f"V_{i}_{a}_{h}",  cat="Integer") for h in range(0,horizonte_h + 1)]   for a in S] for i in N]
Z1 = [[[LpVariable(f"Z1_{i}_{a}_{h}",  cat="Integer") for h in range(0,horizonte_h + 1)]  for a in S] for i in N] 
Z2 =[[[[LpVariable(f"Z2_{i}_{a}_{b}_{h}",  cat="Integer") for h in range(0,horizonte_h + 1)]  for b in S] for a in S]  for i in N]



# Calcular K para todos os estados e decisores
K = [[sum(P[i][a][s] for a in S) for s in S] for i in N]

M = len(S)







# Função objetivo
objective = lpSum(C[i][a][b] for i in N for a in S for b in S if a !=b )

model += objective
#==================== Restrições  =======================

#==================== Restrição 1 =======================

for i in N:
    for a in S:
        for b in S:
            if a != b: #adicionada essa condição para evitar C[i][a][a]
                model += C[i][a][b]*(len(S)-1)*(len(S)-1) >= (W[i][a] - W[i][b]) * (K[i][b] - K[i][a])
       
                    
#==================== Restrição 2 =======================

for i in N:
    for a in S:
        for h in range(1,horizonte_h + 1):
            model += D[i][a][h] + lpSum(Da[i][a][b][h] for b in S if J[i][a][b]==1) == 1

   


#==================== Restrições 9, 10 e 11  - Linearização de  ≠   ======================= 
for i in N:
    for a in S:
        model += lpSum(t[i][a][b] for b in range(len(S))) == 1 


for i in N:
    for a in S:
        model +=  lpSum(b * t[i][a][b] for b in range(len(S))) == W[i][a]


for i in N:
    for b in range(len(S)):
        model += lpSum(t[i][a][b] for a in S) == 1



 #==================== Restrições Baseadas no modelo Matricial Lh - France 2024 =======================           
            

# Restrição 12 e 13 - Inicialização da Matriz B[a][b] de Ganho Antecipado
for i in N:
    for a in S:
        model += V[i][a][0] == W[i][a] # Restrição 12 - Horizonte zero
        for h in range(1, horizonte_h + 1):
            model += B[i][a][a][h] == W[i][a] #  Restrição 19
        for b in S:
            if J[i][a][b] == 1:
                model += B[i][a][b][1] == W[i][b] # Restrição 13 - Horizonte 1
       
for i in N:
    for a in S:
        for b in S:
            if J[i][a][b] == 1:
                for h in range(1, horizonte_h+1):
# Restrições 14, 15, 16 e 17 - Vetor V[a] que armazena o máximo de B para DMi no horizonte h = 1                 
                    model += V[i][a][h] >= B[i][a][b][h]
                    model += V[i][a][h] <= B[i][a][b][h] + (len(S)-1)*(1 - Da[i][a][b][h])
                    model += V[i][a][h] >= W[i][a]
                    model += V[i][a][h] <= W[i][a] + (len(S)-1)*(1 - D[i][a][h])           
                    
# restrição 18 Sugerida já tinha sido inserida
#for i in N:
#    for a in S:
#        for h in range(1,horizonte_h + 1):
#            model += D[i][a][h] + lpSum(Da[i][a][b][h] for b in S ) == 1
                
# Restrições 20  - Recursividade sobre h e Linearização de D[1-i][b][c][h-1]*V[i][c][h-2]
                if horizonte_h >= 2:
                    for h in range(2,horizonte_h + 1):
                        model += B[i][a][b][h] == Z1[i][b][h-1]+ lpSum(Z2[i][b][c][h-1] for c in S if J[1-i][b][c] == 1)
                        # Linearização de Z1 = D[1-i][b][h-1] * W[i][b]

                        model += Z1[i][b][h-1] <= W[i][b]
                        model += Z1[i][b][h-1] <= M * D[1-i][b][h-1]
                        model += Z1[i][b][h-1] >= W[i][b] - M * (1 - D[1-i][b][h-1])
                        model += Z1[i][b][h-1] >= 0

                        # Linearização de Z2 = D[1-i][b][c][h-1] * V[i][c][h-2]
                        for c in S:
                            if J[1-i][b][c]==1:
                                model += Z2[i][b][c][h-1] <= V[i][c][h-2]
                                model += Z2[i][b][c][h-1] <= M * Da[1-i][b][c][h-1]
                                model += Z2[i][b][c][h-1] >= V[i][c][h-2] - M * (1 - Da[1-i][b][c][h-1])
                                model += Z2[i][b][c][h-1] >= 0



# Restrições 21  - condicional if V == W[i][a] then D[i][a][h] == 1 linearizada
for i in N:
    for a in S:
        for h in range(1, horizonte_h + 1):
                # Se V[i][a][h] == W[i][a], então D[i][a][h] = 1
            model += V[i][a][h] - W[i][a]>= 1 - D[i][a][h]   
        # Abaixo estão as restrições antigas que deixavam mutualmente verdadeiras
               # model += V[i][a][h] - W[i][a] == M * ( D[i][a][h] - 1 )
               # model += W[i][a] - V[i][a][h] == M * (1 - D[i][a][h])
        
# Restrição 22 - Condição de equilíbrio
    model += V[i][s][horizonte_h] == W[i][s]


# Resolvendo o modelo
#model.solve(PULP_CBC_CMD(msg=True))
model.solve(CPLEX_CMD(msg=True))
#model.solve()

# Abrindo um arquivo para salvar o relatório completo
with open("resultado_completo.txt", "w") as f:
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
    f.write("\n" + "="*50 + "\n")
    f.write("VARIÁVEIS C_ COM VALOR DIFERENTE DE ZERO:\n")
    f.write("="*50 + "\n")

    for v in model.variables():
        if v.name.startswith("C_") and v.varValue not in (0, None):
            valor = int(v.varValue) if v.varValue in (0.0, 1.0) else v.varValue
            f.write(f"{v.name} = {valor}\n")

    # Exibir separadamente as variáveis sem valor (None)
    f.write("\n" + "="*50 + "\n")
    f.write("VARIÁVEIS SEM VALOR ATRIBUÍDO (None):\n")
    f.write("="*50 + "\n")

    for v in model.variables():
        if v.varValue is None:
            f.write(f"{v.name} = None\n")

    
  
    # MATRIZES DAS VARIÁVEIS Da e D (agrupadas por i e h)
  
    f.write("\n" + "="*60 + "\n")
    f.write("MATRIZES DAS VARIÁVEIS Da E D (POR DECISOR E HORIZONTE):\n")
    f.write("="*60 + "\n")

    # Dicionários para armazenar valores
    Da_values = {}
    D_values = {}

    # Armazenar valores das variáveis Da
    for v in model.variables():
        if v.name.startswith("Da_") and v.varValue is not None:
            parts = v.name.split("_")  # Ex: ['Da', '0', '2', '4', '1']
            i = int(parts[1])
            a = int(parts[2])
            b = int(parts[3])
            h = int(parts[4])
            valor = int(round(v.varValue))

            if i not in Da_values:
                Da_values[i] = {}
            if h not in Da_values[i]:
                Da_values[i][h] = {}
            if a not in Da_values[i][h]:
                Da_values[i][h][a] = {}
            Da_values[i][h][a][b] = valor

    # Armazenar valores das variáveis D
    for v in model.variables():
        if v.name.startswith("D_") and v.varValue is not None:
            parts = v.name.split("_")  # Ex: ['D', '0', '2', '1']
            i = int(parts[1])
            a = int(parts[2])
            h = int(parts[3])
            valor = int(round(v.varValue))

            if i not in D_values:
                D_values[i] = {}
            if h not in D_values[i]:
                D_values[i][h] = {}
            D_values[i][h][a] = valor

    # Escrever os resultados no relatório
    for i in sorted(Da_values.keys()):
        f.write(f"\n{'='*60}\nDECISOR {i}\n{'='*60}\n")
        for h in sorted(Da_values[i].keys()):
            f.write(f"\n--- Horizonte h = {h} ---\n")
            f.write(f"Matriz Da_{i}_a_b_{h} (linhas = a, colunas = b):\n")

            # Cabeçalho das colunas
            estados = sorted({a for a in Da_values[i][h].keys()})
            f.write("      " + " ".join(f"b={b:2}" for b in estados) + "\n")
            f.write("-" * (8 + len(estados) * 5) + "\n")

            # Linhas (estados a)
            for a in estados:
                linha = f"a={a:2} | " + " ".join(f"{Da_values[i][h][a].get(b, 0):2d}" for b in estados)
                f.write(linha + "\n")

            # Mostrar D_i_a_h logo abaixo
            if i in D_values and h in D_values[i]:
                f.write("\nValores de D_%d_a_%d (por estado a):\n" % (i, h))
                for a in sorted(D_values[i][h].keys()):
                    f.write(f"  D_{i}_{a}_{h} = {D_values[i][h][a]}\n")
            else:
                f.write("\nNenhum valor de D encontrado para este horizonte.\n")

    # Exibir os valores das variáveis A organizadas em forma de matriz
    f.write("\n" + "="*50 + "\n")
    f.write("MATRIZES DAS VARIÁVEIS A (POR DECISOR):\n")
    f.write("="*50 + "\n")

    # Dicionário para armazenar os valores de A[i][a][h]
    A_values = {}

    for v in model.variables():
        if v.name.startswith("A_") and v.varValue is not None:
            parts = v.name.split("_")  # Ex: ['A', '0', '3', '2']
            i = int(parts[1])  # decisor
            a = int(parts[2])  # estado
            h = int(parts[3])  # horizonte
            valor = int(round(v.varValue))  # força inteiro

            if i not in A_values:
                A_values[i] = {}
            if a not in A_values[i]:
                A_values[i][a] = {}
            A_values[i][a][h] = valor

    # Escrever cada matriz A_i
    for i in sorted(A_values.keys()):
        f.write(f"\nMatriz A_{i} (linhas = estados, colunas = horizonte):\n")
        # Obter faixas ordenadas
        estados = sorted(A_values[i].keys())
        horizontes = sorted({h for a in estados for h in A_values[i][a].keys()})
        
        # Cabeçalho
        f.write("      " + " ".join(f"h={h:2}" for h in horizontes) + "\n")
        f.write("-" * (8 + len(horizontes) * 5) + "\n")

        # Linhas (estados)
        for a in estados:
            linha = f"a={a:2} | " + " ".join(f"{A_values[i][a].get(h, 0):2d}" for h in horizontes)
            f.write(linha + "\n")

    # Exibir os valores das variáveis W como inteiros
    f.write("\n" + "="*50 + "\n")
    f.write("VALORES DAS VARIÁVEIS W (TODOS):\n")
    f.write("="*50 + "\n")

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




