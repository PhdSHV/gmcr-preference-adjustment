from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus, value, PULP_CBC_CMD, CPLEX_CMD
import math
import numpy
import matplotlib.pyplot as plt
from gmcr_adjustment.solver import solve_model

# Conjuntos
# Definição dos parâmetros

#horizonte_h = 3  # Horizonte de movimento limitado
#S = set(range(5))  # Conjunto de estados
#N = set(range(2))	# Conjunto de decisores
#s = 1										# Estado focal

def ler_csv_inteiros(arquivo):
    matriz = []
    dados = open(arquivo, "r", encoding="utf-8").readlines()
    for linha in dados:
        matriz.append([int(x) for x in linha.split(",")])
    return matriz

def custo_Lh(
        H,
        S,
        N,
        s,
        arquivo_J1,
        arquivo_J2,
        arquivo_P1,
        arquivo_P2
        ,
        solver="auto",
        msg=False
    ):

    horizonte_h = H  # Horizonte de movimento limitado
    S = set(range(S))  # Conjunto de estados
    N = set(range(N))	# Conjunto de decisores
    
    #Ler os arquivos das Acessibilidades dos Decisores:

    J1 = ler_csv_inteiros(arquivo_J1)
    J2 = ler_csv_inteiros(arquivo_J2)
    J = [J1, J2]
    #Ler os arquivos das preferências dos Decisores:
    P1 = ler_csv_inteiros(arquivo_P1)
    P2 = ler_csv_inteiros(arquivo_P2)
    P = [P1, P2]
    

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
                    for c in S:
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
            model += lpSum(t[i][a][b] for a in S) <= 1



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
    solve_model(model, solver=solver, msg=msg)

    #model.solve()
    return value(model.objective)

