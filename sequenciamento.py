# sequenciamento.py
import math
from preprocessamento import checa_dominados, reducao_padroes_por_pseudo_equivalencia, pre_processamento_colapso_grau2
from grafo import Graph,SubGraph

def atualiza_sequencia(sequencia, dicRelacionamentos):
    sequencia_expandida = []
    for padrao in sequencia:
        sequencia_expandida.append(padrao)
        # Adiciona padrões dominados imediatamente após o dominante
        if dicRelacionamentos[padrao] and dicRelacionamentos[padrao] != [-1]:
            sequencia_expandida.extend(dicRelacionamentos[padrao])
    return sequencia_expandida
    

def yuen3ppad(grafo: Graph):
    # inicia pelo padrão com mais peças
    padraoInicial = grafo.selecionaPadraoMaiorQtdPecas()
    Spa = [padraoInicial]
    pecasSpa = set(grafo.obtemPecas(padraoInicial))
    padroesNaoSeq = set(grafo.obtemTodosPadroes()) - {padraoInicial}

    padroesAdjacentes = set()
    for vizinho in grafo.obtemVizinhos(padraoInicial):
        if vizinho in padroesNaoSeq:
            padroesAdjacentes.add(vizinho) 

    qtdPadroes = len(grafo.obtemTodosPadroes())
    while len(Spa) < qtdPadroes:
        padraoEscolhido = None
        maiorM = -math.inf
        menorN = math.inf

        for p in padroesAdjacentes:
            pecasP = set(grafo.obtemPecas(p))
            C = len(pecasP & pecasSpa)       
            N = len(pecasP - pecasSpa)       
            M = C - N
            if M > maiorM:
                padraoEscolhido = p
                maiorM = M
                menorN = N
            elif M == maiorM and N < menorN:
                padraoEscolhido = p
                menorN = N
        if padraoEscolhido is None:
            break
        Spa.append(padraoEscolhido)
        padroesNaoSeq.remove(padraoEscolhido)
        pecasSpa.update(grafo.obtemPecas(padraoEscolhido))

        padroesAdjacentes.remove(padraoEscolhido)

        for vizinho in grafo.obtemVizinhos(padraoEscolhido):
            if vizinho in padroesNaoSeq and vizinho not in padroesAdjacentes:
                padroesAdjacentes.add(vizinho)
    return Spa

if __name__ == '__main__':
    inst = 'Frinhani, Carvalho & Soma/Random-1000-1000-50-7'
    g = Graph(inst)
    
    # Pré-processamento global
    checa_dominados(g)
    print(g.dicRelacionamentos)
    pre_processamento_colapso_grau2(g)
    print(g.dicRelacionamentos)
    reducao_padroes_por_pseudo_equivalencia(g)
    print(g.dicRelacionamentos)
    
    componentes = g.componentesDFS()
    print("Componentes:", componentes)
    
    sequencia_dominantes = []  # Só padrões líderes/donminantes
    for comp in componentes:
        subg = SubGraph(g, comp)
        seq_comp = yuen3ppad(subg)
        sequencia_dominantes.extend(seq_comp)
    
    # EXPANDE a sequência com os dominados
    print("Sequência Dominantes: ",sequencia_dominantes, len(sequencia_dominantes))
    sequencia_final = atualiza_sequencia(sequencia_dominantes, g.dicRelacionamentos)
    
    print("Sequência Yuen3PPad:", sequencia_final)
    nmpa = g.NMPA(sequencia_final)
    print("NMPA: ", nmpa)
