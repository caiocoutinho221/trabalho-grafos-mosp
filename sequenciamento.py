# sequenciamento.py
import math
import numpy as np
from preprocessamento import checa_dominados, reducao_padroes_por_pseudo_equivalencia, pre_processamento_colapso_grau2
from grafo import Graph, SubGraph, desenhaGrafoPadraoPadrao

def PilhasAbertas(LP, graph):
    if len(LP) > 1:
        pa = []
        openStacks = 0
        closedStacks = 0
        maxOpenStacks = -1
        
        # Cria o dicionário de peças com suas frequências
        # (Assumindo que a frequência é quantos padrões contêm cada peça)
        freqPecas = {}
        todas_pecas = graph.obtemTodasPecas()
        for peca in todas_pecas:
            freqPecas[peca] = sum(1 for p in graph.obtemTodosPadroes() 
                                if peca in graph.obtemPecas(p))
        
        pilhas = {x: 0 for x in todas_pecas}  # Vetor que controla se a pilha foi aberta ou não
        
        for padrao in LP:  # Para cada padrao em LP
            pecas = graph.obtemPecas(padrao)
            for pe in pecas: # Para cada peca (pe) do padrão pad
                freqPecas[pe] = freqPecas[pe] - 1
                if freqPecas[pe] == 0: #Se SIM todas as peças já foram empilhadas
                    closedStacks += 1
                if pilhas[pe] == 0: # Se a pilha ainda não foi aberta
                    openStacks += 1
                    pilhas[pe] = 1 # Marca pilha como aberta
                    
            if openStacks > maxOpenStacks:
                maxOpenStacks = openStacks
            pa.append(openStacks)
            openStacks -= closedStacks #Atualiza pilhas abertas retirando as que foram fechadas
            closedStacks = 0
        return pa
    else: # Para o caso de uma matriz com uma só coluna.
        Q = graph.matPadraoPeca[LP, :]
        pa = [np.sum(Q)]
        return pa

def MMOSP(LP, grafo: Graph):
    vetor = PilhasAbertas(LP, grafo)
    mosp = np.amax(vetor) # Obtem a maior pilha do vetor
    somatorioMOSP = np.sum(vetor)
    MMOSP = mosp + (somatorioMOSP / (len(vetor) * mosp))
    return MMOSP

def atualiza_sequencia(sequencia, dicRelacionamentos):
    sequencia_expandida = []
    for padrao in sequencia:
        sequencia_expandida.append(padrao)
        # Adiciona padrões dominados imediatamente após o dominante
        if dicRelacionamentos[padrao] and dicRelacionamentos[padrao] != [-1]:
            sequencia_expandida.extend(dicRelacionamentos[padrao])
    return sequencia_expandida

# Calcula o númer maximo de pilhas abertas (substituir por mmosp)
def NMPA(LP, grafo: Graph):
    if len(LP) > 1:
        Q = grafo.matPadraoPeca[LP, :]
        Q = np.maximum.accumulate(Q, axis=0) & np.maximum.accumulate(Q[::-1, :], axis=0)[::-1, :]
        pa = np.sum(Q, 1)
    else: # Apenas usado no caso de matrizes com uma só coluna.
        Q = grafo.matPadraoPeca[LP, :]
        pa = [np.sum(Q)]
    return np.amax(pa) # Obtém a maior pilha do vetor

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

def executaYuenPreProcessado(grafo: Graph):
    componentes = grafo.componentesDFS()

    sequencia_dominantes = []  # Só padrões líderes/donminantes
    for comp in componentes:
        subg = SubGraph(grafo, comp)
        seq_comp = yuen3ppad(subg)
        sequencia_dominantes.extend(seq_comp)
    
    # EXPANDE a sequência com os dominados
    print("Sequência Dominantes: ",sequencia_dominantes, len(sequencia_dominantes))
    sequencia_final = atualiza_sequencia(sequencia_dominantes, grafo.dicRelacionamentos)
    return sequencia_final
