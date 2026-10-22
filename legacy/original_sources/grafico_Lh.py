import matplotlib.pyplot as plt
from custo_Lh import custo_Lh

custos=[]

horizontes = list(range(1,3))
total_estados = 12  # Conjunto de estados
total_decisores = 2	# Conjunto de decisores
estado_focal = 1				# Estado focal
for h in horizontes:
       
    custo = custo_Lh(
        H=h,
        S = total_estados,
        N = total_decisores,
        s = estado_focal,
        arquivo_J1="J1-12est.csv",
        arquivo_J2="J2-12est.csv",
        arquivo_P1="P1-12est.csv",
        arquivo_P2="P2-12est.csv"
    )
    custo_inteiro=int(custo)
    print("\n>>> Custo para {s} ser Lh estável com horizonte {h}:")
    print("Custo retornado =", custo)
    custos.append(custo_inteiro)
print("\n>>> Os custos obtidos para {s} ser Lh estável com horizonte {h}:", custos)

plt.figure(figsize=(8,5))
plt.plot(horizontes, custos, marker='o')
plt.xlabel("Horizonte h")
plt.xticks([int(h) for h in horizontes])
plt.ylabel("Custo para tornar o estado s estável")
plt.title("Gráfico Custo x Horizonte para o estado {estado_focal}")
plt.grid(True)
nome_arquivo = f"grafico_conflito_com_{total_estados}_estados_estado_focal_{estado_focal}_ate_{max(horizontes)}_horizontes.png"
plt.savefig(nome_arquivo, dpi=300)
plt.show()


