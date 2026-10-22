# Importando as bibliotecas necessárias
import cvxpy as cp
import numpy as np


# Conflito com 2 decisores
N=2
# Número de estados do conflito
m=int(input('Digite o número de estados do conflito: '))

# Inicializando as matrizes vazias de preferências, acessibilidades e alterações dos decisores
P = []
R = []
X = cp.Variable((m, m), integer=True)   

# Solicite os valores da matriz de preferências
for k in range(N):  # 2 camadas
    print(f"Digite os valores da matriz das preferências do decisor {k + 1} => P({k+1}x{m}x{m}):")
    camada = []
    for i in range(m):  # m linhas por camada
        linha = list(map(int, input(f"  Linha {i + 1}, separada por espaço: ").split()))
        camada.append(linha)
    P.append(camada)
    
# Solicite os valores da matriz de acessibilidade
for k in range(N):  # 2 camadas
    print(f"Digite os valores da matriz das preferências do decisor {k + 1} => R({k+1}x{m}x{m}):")
    camada = []
    for i in range(m):  # m linhas por camada
        linha = list(map(int, input(f"  Linha {i + 1}, separada por espaço: ").split()))
        camada.append(linha)
    R.append(camada)    

#Estado focal
s = int(input(f'Digite o estado focal s tal que s é maior que 1 e menor que {m}'))

#Critério de estabilidade
criterio = int(input('Digite o critério de estabilidade(1-GMR): '))

# Mostre as matrizes de preferências resultante
print("\n R:")
for k in range(N):
    print(f"Acessibilidade do decisor {k + 1}:")
    for linha in R[k]:
        print(linha)
        
# Mostre as matrizes de acessibilidade resultante
print("\n P:")
for k in range(N):
    print(f"Preferências do decisor {k + 1}:")
    for linha in P[k]:
        print(linha)
  


     