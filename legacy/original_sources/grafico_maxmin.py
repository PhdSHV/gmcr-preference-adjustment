import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from custo_maxmin import custo_maxmin



custos=[]

horizontes = list(range(1,11))
total_estados = 5  # Conjunto de estados
total_decisores = 2	# Conjunto de decisores
estado_focal = 1				# Estado focal
for h in horizontes:
       
    custo = custo_maxmin(
        H=h,
        S = total_estados,
        N = total_decisores,
        s = estado_focal,
        arquivo_J1="J1-5est.csv",
        arquivo_J2="J2-5est.csv",
        arquivo_P1="P1-5est.csv",
        arquivo_P2="P2-5est.csv"
    )
   
    custo_inteiro=int(round(custo))
    print(f"\n>>> Custo para o estado {estado_focal} ser Maxmin estável com horizonte {h}:")
    print("Custo retornado =", custo_inteiro)
    custos.append(custo_inteiro)
print(f"\n>>> Os custos obtidos para o estado {estado_focal} ser Maxmin estável com horizonte {h}:", custos)

plt.figure(figsize=(8,5))
plt.plot(horizontes, custos, marker='o', zorder=3, linewidth=2)
plt.xlabel("Horizonte h")
ax = plt.gca()
ax.spines['bottom'].set_zorder(1)
plt.xticks([int(h) for h in horizontes])
plt.ylabel(f"Custo para tornar o estado {estado_focal} estável")
plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
ax = plt.gca()

#  eixo y nunca negativo
ax.set_ylim(bottom=0)

#  força ticks inteiros
ax.yaxis.set_major_locator(MaxNLocator(integer=True))

# caso especial: todos os custos iguais
if min(custos) == max(custos):
    valor = custos[0]
    ax.set_ylim(0, max(1, valor + 1))
    ax.set_yticks(range(0, valor + 2))
plt.title(f"Gráfico Custo x Horizonte para o estado {estado_focal}")
plt.grid(True)
nome_arquivo = f"grafico_conflito_com_{total_estados}_estados_estado_focal_{estado_focal}_ate_{max(horizontes)}_horizontes.png"
plt.savefig(nome_arquivo, dpi=300)
plt.show()


