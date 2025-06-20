# preprocessamento.py
from grafo import Graph

# Técnica de redução por pseudo equivalência
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
    
    if gruposFinais:
        dicRelacionamentos = grafo.dicRelacionamentos
        nova_lista = []
        for grupo in gruposFinais:
            lider = grupo[0]
            nova_lista = list(grupo[1:])

            for i in grupo[1:]:
                if dicRelacionamentos[i] != []:
                    nova_lista.extend(dicRelacionamentos[i])
                dicRelacionamentos[i] = [-1]

            dicRelacionamentos[lider] = nova_lista

        grafo.alteraRelacao(dicRelacionamentos)

# Técnica de redução por dominância
def checa_dominados(grafo: Graph):
    
    # 1) copia o relacionamento atual
    nova_rel = {p: list(v) for p, v in grafo.dicRelacionamentos.items()}

    padroes   = list(grafo.dicPadroes.keys())
    dominados = set()
    dominantes = {}

    # 2) detecção de dominações diretas
    for p1 in padroes:
        if p1 in dominados:
            continue
        set1 = set(grafo.dicPadroes[p1])
        for p2 in padroes:
            if p1 == p2 or p2 in dominados:
                continue
            set2 = set(grafo.dicPadroes[p2])

            if set1.issubset(set2) and set1 != set2:
                dominantes.setdefault(p2, []).append(p1)
                dominados.add(p1)
                break
            elif set2.issubset(set1) and set1 != set2:
                dominantes.setdefault(p1, []).append(p2)
                dominados.add(p2)

    """print(dominados)
    print(dominantes)"""
    # 3) fechamento transitivo: quem domina herda todos os dominados de seus filhos
    def _dfs(node, acc):
        for filho in dominantes.get(node, []):
            if filho not in acc:
                acc.add(filho)
                _dfs(filho, acc)
        return acc

    for dom in list(dominantes):
        transitivos = sorted(_dfs(dom, set()))
        dominantes[dom] = transitivos

    # 4) preenche a cópia com as regras finais
    #    quem domina tem a lista completa; quem é dominado vira [-1]
    for p in padroes:
        nova_rel[p] = []              # limpa
    for dom, filhos in dominantes.items():
        nova_rel[dom] = filhos.copy()
    for d in dominados:
        nova_rel[d] = [-1]
    # 5) aplica na instância
    grafo.alteraRelacao(nova_rel)

# Técnica de redução por colapso de grau 2
def pre_processamento_colapso_grau2(grafo: Graph):
    padroes = grafo.obtemTodosPadroes()
    relacao = {p: [] for p in padroes}  # Inicialmente, todos são listas vazias
    pares_colapsados = []

    # Passo 1: Identifica pares (p, q) onde ambos têm grau 2 e são vizinhos
    for p in padroes:
        vizinhos_p = set(grafo.obtemVizinhos(p))
        if len(vizinhos_p) == 2:
            for q in vizinhos_p:
                vizinhos_q = set(grafo.obtemVizinhos(q))
                if len(vizinhos_q) == 2 and p < q and p in vizinhos_q:
                    pares_colapsados.append((p, q))

    relacao = grafo.dicRelacionamentos
    # Passo 2: Processa os pares
    for p, q in pares_colapsados:
        # Se p ou q já estão colapsados ([-1]), ignora
        if (isinstance(relacao[p], list) and len(relacao[p])) > 0 and relacao[p][0] == -1:
            continue
        if (isinstance(relacao[q], list) and len(relacao[q])) > 0 and relacao[q][0] == -1:
            continue

        # Adiciona q aos dominados por p
        relacao[p].append(q)

        # Se q já dominava outros, transfere para p
        if isinstance(relacao[q], list) and len(relacao[q]) > 0 and relacao[q][0] != -1:
            relacao[p].extend(relacao[q])

        # Marca q como colapsado ([-1])
        relacao[q] = [-1]

    # Remove duplicatas e ordena ([-1])
    for k in relacao:
        if isinstance(relacao[k], list) and len(relacao[k]) > 0 and relacao[k][0] != -1:
            relacao[k] = sorted(set(relacao[k]))
    grafo.alteraRelacao(relacao)