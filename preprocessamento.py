# preprocessamento.py
from grafo import Graph

def reducao_padroes_por_pseudo_equivalencia(grafo: Graph):
    vizinhos = {}
    nroPadroes = len(grafo.matPadraoPadrao)
    # Chaves vão ser os padrões existentes
    # conteudo de cada chave vai ser os seus vizinhos
    for i in range(nroPadroes):
        vizinhos[i] = grafo.obtemVizinhos(i)


    # Agora o dicionario vizinhos possui os vizinhos de cada padrao
    # Preciso identificar quais padroes possuem lista de vizinhos iguais
    # a lista retornada por obtemVizinhos contém os indices dos padrões e está ordenada.

    gruposFinais = []

    # váriavel para indicar se um padrão ja pertence a algum grupo
    usado = [False] * nroPadroes

    for i in range(nroPadroes):

        if usado[i]:
            continue
    
        # Vamos tentar construir um grupo, começamos adicionando o proprio vertice em que estamos
        grupoAtual = [i]

        viz_i = vizinhos[i]
        # Vamos analisar se os vizinhos de i possuem a mesma vizinhança que ele
        for j in viz_i:
            if usado[j]:
                continue

            # Vamos comparar as listas de vizinhanças
            if viz_i != vizinhos[j]:
                continue # vizinhanças diferentes, ignoro e vou pro proximo

            # Caso possuam vizinhanças identicas, vamos analisar se as peças também são iguais
            # Vamos na matriz original,e para cada vizinho r (na lista de viz_i) analisamos se
            # matriz[i,r] == matriz[j,r] -> lembrando que na matriz, uma celula contem uma lista 
            # com as peças que os padroes compartilham
            valido = True
            for r in viz_i:
                if grafo.matPadraoPadrao[i,r] != grafo.matPadraoPadrao[j,r]:
                    valido = False
                    break
            
            if valido:
                grupoAtual.append(j)
                usado[j] = True
        
        # Verificamos se o grupo atual é formado por mais algum padrão sem ser o i
        if (len(grupoAtual) > 1):
            gruposFinais.append(grupoAtual)

        # Podemos marcar o i como usado para evitar ficar pesquisando
        usado[i] = True
    
    return gruposFinais

def checa_dominados(grafo: Graph):
    padroes = list(grafo.dicPadroes.keys())
    dominados = set()
    dominantes = {}
    
    for i in range(len(padroes)):
        p1 = padroes[i]
        if p1 in dominados:
            continue
        
        for j in range(len(padroes)):
            if i == j:
                continue
            
            p2 = padroes[j]
            set1 = set(grafo.dicPadroes[p1])
            set2 = set(grafo.dicPadroes[p2])
            
            # verifica se o padrão 1 é subconjunto do padrão 2 ou vice-versa
            if set1.issubset(set2) and set1 != set2:
                if p2 in dominantes.keys():
                    dominantes[p2].append(p1)
                else:
                    dominantes[p2] = [p1]
                dominados.add(p1)
                break
            
            elif set2.issubset(set1) and set1 != set2:
                if p1 in dominantes.keys():
                    dominantes[p1].append(p2)
                else:
                    dominantes[p1] = [p2]
                dominados.add(p2)
    
    return sorted(dominados), dominantes
