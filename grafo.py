import numpy as np
import math

class Graph():
    def __init__(self, instancia):
        self.__instanciaOriginaria = './datasets/' + instancia
        self._matPadraoPeca = self.__criaMatPadraoPeca(self.__instanciaOriginaria)
        self._matPadraoPadrao = self.__criaMatPadraoPadrao(self.__instanciaOriginaria)
        self._dicionarioPadroes = self.montarDictPadroes(self.__instanciaOriginaria)

    @property
    def dicPadroes(self):
        return self._dicionarioPadroes    
    
    def __criaMatPadraoPeca(self, instancia):
        caminho = instancia + '.txt'
        with open(caminho, 'rb') as f:
            nrows, ncols = [int(field) for field in f.readline().split()]
            data = np.genfromtxt(f, dtype="int32", max_rows=nrows) #OBS. Instancias estao no formato padrao x peca
        return data
    
    def __criaMatPadraoPadrao(self, instancia):
        caminho = instancia + '.txt'
        with open(caminho, 'rb') as f:
            #pega as dimensoes, no ex1 o rows é 14 e o cols 8
            # Ta no formato padrao x peça, temos que colocar em um matriz quadrada nrows x nrows e incluir 
            # entre os elementos as peças como arestas
            nrows, ncols = [int(field) for field in f.readline().split()]
            data = np.genfromtxt(f, dtype="int32", max_rows=nrows) #OBS. Instancias estao no formato padrao x peca
            # depois de gerar a matriz original, vamos criar a nova:
            # padrao x padrao
            data_shape = (nrows, nrows)
            arr = np.empty(data_shape, dtype=object)
            for index in range(nrows):
                for index2 in range(nrows):
                    arr[index, index2] = []
            
            # agora para cada peça (col na antiga) passamos pelas linhas e incluimos aquela peça na aresta
            for peca in range(ncols):
                previous_padroes = []
                for padrao in range(nrows):
                    if data[padrao][peca]:
                        for prev_pad in previous_padroes:
                            arr[padrao, prev_pad].append(peca)
                            arr[prev_pad, padrao].append(peca)  # Bidirecional
                        previous_padroes.append(padrao)
                        
        return arr
        
    def montarDictPadroes(self, instancia):
        padroes_d = {}
        m = self._matPadraoPeca
        l, c = m.shape
        for x in range(l):
            padroes_d[x] = [y for y in range(c) if m[x][y]]
            
        return padroes_d
    
    def obtemPecas(self, padrao):
        if(not self._dicionarioPadroes):
            self._dicionarioPadroes = self.montarDictPadroes(self.__instanciaOriginaria)
        return self._dicionarioPadroes[padrao]
    
    # discutir criterio de desempate
    def selecionaPadraoMaiorQtdPecas(self):
        return max(self._dicionarioPadroes, key=lambda k: len(self._dicionarioPadroes[k]))
    
    # lista dos vertices?
    def obtemTodosPadroes(self):
        return list(range(len(self._matPadraoPadrao)))
    
    def obtemVizinhos(self, padrao):
        vizinhos = []
        size = len(self._matPadraoPadrao)
        for p in range(size):
            if len(self._matPadraoPadrao[padrao][p]) > 0:
                vizinhos.append(p)
                
        return vizinhos
    
    
    def NMPA(self, LP):
        if len(LP) > 1:
            Q = self._matPadraoPeca[LP, :]
            Q = np.maximum.accumulate(Q, axis=0) & np.maximum.accumulate(Q[::-1, :], axis=0)[::-1, :]
            pa = np.sum(Q, 1)
        else: # Apenas usado no caso de matrizes com uma só coluna.
            Q = self._matPadraoPeca[LP, :]
            pa = [np.sum(Q)]
        return np.amax(pa) # Obtém a maior pilha do vetor
    
    def salvarMatriz(self, nomeArquivo):
        formatted_output = []
        for row in self._matPadraoPadrao:
            formatted_row = ' '.join(str(elem) for elem in row)
            formatted_output.append(formatted_row)
        
        output_file = nomeArquivo + '.txt'
        with open(output_file, 'w') as f:
            for line in formatted_output:
                f.write(line + '\n')
    

''' 
Problema: MOSP (Minimization of Open Stacks Problem)
Descrição: Gera a sequência de padrões utilizando a yuen 3 normal adaptada para se limitar aos vizinhos
Entrada: Objeto do tipo Graph
Saída: Lista com a sequência de padrões no formato ndarray
'''
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



# exemplo de execução
grafo = Graph('Chu_Stuckey/Random-50-100-8-5')
sequencia = yuen3ppad(grafo)
print(grafo.NMPA(sequencia))
print(sequencia)