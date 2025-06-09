# grafo.py
import numpy as np
import math

class Graph():
    def __init__(self, instancia):
        self.__instancia = './datasets/' + instancia
        self.__matPadraoPeca = self.__criaMatPadraoPeca(self.__instancia)
        self.__matPadraoPadrao = self.__criaMatPadraoPadrao(self.__instancia)
        self.__dicionarioPadroesPecas = self.__montarDicionarioPadroesPecas()
        self.__dicionarioRelacionamentos = self.__criaRelacionamentos()
        
        
    # Inicializa um dicionario que vai ser alterado pelos pré-processamentos. Caso o padrão esteja como vazio, o padrão
    # deve ser tratado normalmente no sequenciamento. Caso seja -1, ele deve ser ignorado, já que será sequenciado posteriormente
    # por alguma relação de dominância ou agrupamento. Por último, caso seja uma lista com elementos, ela representa os padrões 
    # dominados pelo padrão que a contém.
    def __criaRelacionamentos(self):
        dicionario = {}
        padroes = self.obtemTodosPadroes()
        for padrao in padroes:
            dicionario[padrao] = []
        return dicionario
    
    # Os pré-processamentos receberão uma cópia do dicionário original, depois de alterá-lo, forçará uma atualização na estrutura
    # do grafo atualizando o dicionário com as alterações feitas
    def alteraRelacao(self, novoDicionario):
        self.__dicionarioRelacionamentos = novoDicionario
            
    @property
    def dicPadroes(self):
        return self.__dicionarioPadroesPecas
    
    @property
    def dicRelacionamentos(self):
        return self.__dicionarioRelacionamentos
    
    @property
    def matPadraoPadrao(self):
        return self.__matPadraoPadrao     
    
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

            # ************* O código acima é o mesmo da função __criaMataPadraoPadrao Analisar isso

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

    # Constrói um dicionário contendo:
    # [Padrão] -> [Peças]    
    def __montarDicionarioPadroesPecas(self):
        padroes_d = {}
        m = self.__matPadraoPeca
        l, c = m.shape
        for x in range(l):
            padroes_d[x] = [y for y in range(c) if m[x][y]]
            
        return padroes_d
    
    # Retorna as peças associadas a um padrão, por meio do dicionarioPadroes
    def obtemPecas(self, padrao):
        return self.__dicionarioPadroesPecas[padrao]
    
    # discutir criterio de desempate
    # Retorna o padrao que contem a maior quantidade de peças
    def selecionaPadraoMaiorQtdPecas(self):
        return max(self.__dicionarioPadroesPecas, key=lambda k: len(self.__dicionarioPadroesPecas[k]))
    
    # lista dos vertices?
    def obtemTodosPadroes(self):
        return list(range(len(self.__matPadraoPadrao)))
    

    # Retorna uma lista contendo todos os padroes adjacentes ao padrao recebido
    def obtemVizinhos(self, padrao):
        vizinhos = []
        size = len(self.__matPadraoPadrao)
        for p in range(size):
            if len(self.__matPadraoPadrao[padrao][p]) > 0:
                vizinhos.append(p)
                
        return vizinhos
    
    # Calcula o númer maximo de pilhas abertas (substituir por mmosp)
    def NMPA(self, LP):
        if len(LP) > 1:
            Q = self.__matPadraoPeca[LP, :]
            Q = np.maximum.accumulate(Q, axis=0) & np.maximum.accumulate(Q[::-1, :], axis=0)[::-1, :]
            pa = np.sum(Q, 1)
        else: # Apenas usado no caso de matrizes com uma só coluna.
            Q = self.__matPadraoPeca[LP, :]
            pa = [np.sum(Q)]
        return np.amax(pa) # Obtém a maior pilha do vetor
    
    def salvarMatriz(self, nomeArquivo):
        formatted_output = []
        for row in self.__matPadraoPadrao:
            formatted_row = ' '.join(str(elem) for elem in row)
            formatted_output.append(formatted_row)
        
        output_file = nomeArquivo + '.txt'
        with open(output_file, 'w') as f:
            for line in formatted_output:
                f.write(line + '\n')
    
    # DFS para identificar as componentes do grafo
    # Podemos tratar as componentes de maneira independente, por isso as identificamos
    # Função retorna uma lista contendo as componentes do grafo
    def componentesDFS(self):
        componentes = []
        idVertices = self.obtemTodosPadroes()
        visitados = []
        pilha = [0]
        componenteAtual = []
        while pilha:
            atual = pilha.pop()
            
            if atual not in visitados:
                visitados.append(atual)
                idVertices.remove(atual)
                componenteAtual.append(atual)
                
            for vizinho in reversed(self.obtemVizinhos(atual)):
                if vizinho not in visitados:
                    pilha.append(vizinho)

            
            if len(pilha) == 0 and len(idVertices) != 0:
                pilha.append(idVertices[0])
                if componenteAtual:
                    componentes.append(componenteAtual)
                    componenteAtual = []
        
        # Caso único quando há apenas uma componente
        if componenteAtual: componentes.append(componenteAtual)
        return componentes
