# sequenciamento.py
import math
from preprocessamento import checa_dominados, reducao_padroes_por_pseudo_equivalencia
from grafo import Graph

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
    inst = 'Testes/Cenário 3 - 1 - exemplo'
    g = Graph(inst)
    reducao_padroes_por_pseudo_equivalencia(g)
    print("Componentes:", g.componentesDFS())
    seq = yuen3ppad(g)
    print("Sequência Yuen3PPad:", seq)
