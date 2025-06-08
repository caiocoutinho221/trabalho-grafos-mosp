import numpy as np
import math

class Graph():
    def __init__(self, instancia):
        self.__instancia = './datasets/' + instancia
        self.__matPadraoPeca = self.__criaMatPadraoPeca(self.__instancia)
        self.__matPadraoPadrao = self.__criaMatPadraoPadrao(self.__instancia)
        self.__dicionarioPadroes = self.__montarDicionarioPadroes(self.__instancia)

    @property
    def dicPadroes(self):
        return self.__dicionarioPadroes
    
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
    def __montarDicionarioPadroes(self):
        padroes_d = {}
        m = self.__matPadraoPeca
        l, c = m.shape
        for x in range(l):
            padroes_d[x] = [y for y in range(c) if m[x][y]]
            
        return padroes_d
    
    # Retorna as peças associadas a um padrão, por meio do dicionarioPadroes
    def obtemPecas(self, padrao):
        return self.__dicionarioPadroes[padrao]
    
    # discutir criterio de desempate
    # Retorna o padrao que contem a maior quantidade de peças
    def selecionaPadraoMaiorQtdPecas(self):
        return max(self.__dicionarioPadroes, key=lambda k: len(self.__dicionarioPadroes[k]))
    
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
        
        return componentes
    

''' 
Problema: MOSP (Minimization of Open Stacks Problem)
Descrição: Técnica de Pré-Processamento 5/6 _ Redução de pseudoPadrões. Analisa a vizinhança, caso exista padrões
com vizinhanças iguais, para vizinhos e peças, forma um grupo que deve ser agrupado posteriormente
Entrada: Objeto do tipo Graph
Saída: Lista contendo os grupos que podem ser reduzidos
'''
def reducaoPadroesPorPseudoEquivalencia(grafo : Graph):
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