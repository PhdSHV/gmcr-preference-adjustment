from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus, value, PULP_CBC_CMD, CPLEX_CMD
import math
import numpy
import matplotlib.pyplot as plt

# Conjuntos
# Definição dos parâmetros

#horizonte_h = 3  # Horizonte de movimento limitado
#S = set(range(5))  # Conjunto de estados
#N = set(range(2))	# Conjunto de decisores
#s = 1										# Estado focal

def ler_csv_inteiros(arquivo):
    matriz = []
    dados = open(arquivo, "r").readlines()
    for linha in dados:
        matriz.append([int(x) for x in linha.split(",")])
    return matriz

def custo_maxmin(
        H,
        S,
        N,
        s,
        arquivo_J1,
        arquivo_J2,
        arquivo_P1,
        arquivo_P2
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
    D = [[[[LpVariable(f"D_{i}_{j}_{a}_{h}", 0, 1, cat="Binary") for h in range(0,horizonte_h+1)]  for a in S] for j in N] for i in N]
    Da =[[[[[LpVariable(f"Da_{i}_{j}_{a}_{b}_{h}", 0, 1, cat="Binary") for h in range(0,horizonte_h+1)]  for b in S] for a in S]  for j in N] for i in N]
    W = [[LpVariable(f"W_{i}_{a}", cat="Integer") for a in S] for i in N]
    A = [[[[LpVariable(f"A_{i}_{j}_{a}_{h}", cat="Integer") for h in range(0,horizonte_h +1)] for a in S] for j in N] for i in N]
    t = [[[LpVariable(f"t_{i}_{a}_{b}", 0,1,cat="Binary") for b in S] for a in S] for i in N]
     


    # Calcular K para todos os estados e decisores
    K = [[sum(P[i][a][s] for a in S) for s in S] for i in N]

    M = len(S)







        # Função objetivo# Função objetivo
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
           
    #==================== Restrições 2, 3, 4 e 5 =======================     


    for i in N:
        for a in S:
            for h in range(1,horizonte_h + 1):
                model += A[i][i][a][h] >= W[i][a]
                model += A[i][i][a][h] <= W[i][a] + (len(S)-1) * (1 - D[i][i][a][h])
                model += A[i][1-i][a][h] <= W[i][a]
                model += A[i][1-i][a][h] >= W[i][a] - (len(S)-1) * (1 - D[i][1-i][a][h])
    #==================== Restrições 6, 7, 8 e 9 ======================= 

    for i in N:
        for a in S:
            for b in S:
                 for h in range(1,horizonte_h + 1): 
                     if J[i][a][b]==1:   
                        model += A[i][i][a][h] >= A[i][1-i][b][h-1]
                        model += A[i][i][a][h] <= A[i][1-i][b][h-1] + (len(S)-1)*(1 - Da[i][i][a][b][h])
                     if J[1-i][a][b] == 1: 
                        model += A[i][1-i][a][h] <= A[i][i][b][h-1]
                        model += A[i][1-i][a][h] >= A[i][i][b][h-1] - (len(S)-1) * (1 - Da[i][1-i][a][b][h])



    #==================== Restrição 10 ======================= SERÁ SEPARADA EM DUAS RESTRIÇÕES PARA ABRANGER O CASO MULTI DM - VER E-MAIL AJUSTES DO ORIENTADOR DIA 30/03/2026
    for i in N:
        for j in N:
            for a in S:
                for h in range(1,horizonte_h + 1):
                    model += D[i][j][a][h] + lpSum(Da[i][j][a][b][h] for b in S if J[j][a][b]==1 ) == 1

        
        




    #==================== Restrições 11, 12 e 13 ======================= 
    for i in N:
       
        model += A[i][i][s][horizonte_h] == W[i][s] # restrição de estabilidade


    # Calcular A inicial (h=0) para todos os estados e decisores 
    for i in N:
        for a in S:
            model += A[i][i][a][0] == W[i][a]   # restrição 1 de inicialização
            model += A[i][1-i][a][0] == W[i][a] # restrição 1 de inicialização


    # Restrição 14
    for i in N:
        for a in S:
            model += lpSum(t[i][a][b] for b in range(len(S))) == 1 # , f"Restricao_10_{i}_{a}"

    # Restrição 15
    for i in N:
        for a in S:
            model +=  lpSum(b * t[i][a][b] for b in range(len(S))) == W[i][a]#, f"Restricao_11_{i}_{a}"

    # Restrição 16
    for i in N:
        for b in range(len(S)):
            model += lpSum(t[i][a][b] for a in S) <= 1#, f"Restricao_12_{i}_{b}"


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
    #model.solve(PULP_CBC_CMD(msg=True))
    model.solve(CPLEX_CMD(msg=False))

    status = LpStatus[model.status]

    if status != "Optimal":
        return None, status, None

    W_values = {}

    for v in model.variables():
        if v.name.startswith("W_") and v.varValue is not None:

            partes = v.name.split("_")
            i = int(partes[1])
            a = int(partes[2])

            valor = int(round(v.varValue))

            if i not in W_values:
                W_values[i] = {}

            W_values[i][a] = valor

    return value(model.objective), status, W_values

if __name__ == "__main__":

    
    fo, status, W = custo_maxmin_indiferenca(
        H=2,
        S=5,
        N=2,
        s=1,
        arquivo_J1="J1-5est.csv",
        arquivo_J2="J2-5est.csv",
        arquivo_P1="P1-5est.csv",
        arquivo_P2="P2-5est.csv"
    )

    print("Status =", status)
    print("FO =", fo)
    print("W =", W)
