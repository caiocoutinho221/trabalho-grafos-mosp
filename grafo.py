# grafo.py
import numpy as np
from igraph import Graph as igraph, plot

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
    def matPadraoPeca(self):
        return self.__matPadraoPeca
    
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
    
    def obtemTodasPecas(self):
        padroes, pecas = self.matPadraoPeca.shape
        return list(range(pecas))
    
    def obtemDensidade(self):
        v, a = self.contarVerticesArestas()
        return f"{2*a / ((v-1) * v):.3f}"
    
    # Retorna uma lista contendo todos os padroes adjacentes ao padrao recebido
    def obtemVizinhos(self, padrao):
        vizinhos = []
        size = len(self.__matPadraoPadrao)
        for p in range(size):
            if len(self.__matPadraoPadrao[padrao][p]) > 0:
                vizinhos.append(p)
                
        return vizinhos
    
    def salvarMatriz(self, nomeArquivo="generico"):
        formatted_output = []
        for row in self.__matPadraoPadrao:
            formatted_row = ' '.join(str(elem).replace(" ", "") for elem in row)
            formatted_output.append(formatted_row)
        
        output_file = nomeArquivo + '.txt'
        with open(output_file, 'w') as f:
            for line in formatted_output:
                f.write(line + '\n')
                
    def contarVerticesArestas(self):
        validos = [i for i in self.obtemTodosPadroes() if self.dicRelacionamentos[i] != [-1]]
        num_vertices = len(validos)
        num_arestas = 0
        mat = self.matPadraoPadrao
        for idx, i in enumerate(validos):
            for j in validos[idx+1:]:
                if len(mat[i, j]) > 0:
                    num_arestas += 1
        return num_vertices, num_arestas
    
    # DFS para identificar as componentes do grafo
    # Podemos tratar as componentes de maneira independente, por isso as identificamos
    # Função retorna uma lista contendo as componentes do grafo
    def componentesDFS(self):
        # Considera apenas padrões que não foram removidos (não estão marcados como [-1])
        padroes_ativos = [p for p in self.obtemTodosPadroes() if self.dicRelacionamentos[p] != [-1]]
        visitados = set()
        componentes = []
        
        for padrao in padroes_ativos:
            if padrao not in visitados:
                componente = []
                pilha = [padrao]
                
                while pilha:
                    atual = pilha.pop()
                    if atual not in visitados:
                        visitados.add(atual)
                        componente.append(atual)
                        # Adiciona vizinhos não removidos e não visitados
                        for vizinho in self.obtemVizinhos(atual):
                            if (vizinho in padroes_ativos and 
                                vizinho not in visitados and 
                                self.dicRelacionamentos[vizinho] != [-1]):
                                pilha.append(vizinho)
                
                if componente:
                    componentes.append(componente)
                    
        return componentes

class SubGraph:
    def __init__(self, grafo_original, lista_padroes):
        self.original = grafo_original
        self.padroes = lista_padroes   # Padrões da componente

    def obtemTodosPadroes(self):
        return self.padroes

    def obtemPecas(self, padrao):
        return self.original.obtemPecas(padrao)

    def obtemVizinhos(self, padrao):
        # Filtra apenas vizinhos presentes na componente
        return [v for v in self.original.obtemVizinhos(padrao) 
                if v in self.padroes]

    def selecionaPadraoMaiorQtdPecas(self):
        return max(self.padroes, 
                   key=lambda p: len(self.original.obtemPecas(p)))

    def NMPA(self, LP):
        return self.original.NMPA(LP)
    
def desenhaGrafoPadraoPadrao(grafo: Graph, nomeArq = "generico"):
    lista_dominados = []
    dominantes = {}
    # Popula arrays de dominantes e dominados
    for x in grafo.dicRelacionamentos.keys():
        if len(grafo.dicRelacionamentos[x]) > 0:
            if grafo.dicRelacionamentos[x][0] == -1:
                lista_dominados.append(x)
            else:
                dominantes[x] = grafo.dicRelacionamentos[x]

    print(f"dominados: {lista_dominados}\n")
    print(f"DOMINANES: {dominantes}\n")
    
    # Cria a matriz padrão x padrão
    matriz = grafo.matPadraoPadrao
    nrows = matriz.shape[0]
    
    # Cria o grafo
    g = igraph()
    
    validos = [nrow for nrow in range(nrows) if nrow not in lista_dominados]
    print(f"Validos: {validos}")
    # Adiciona os vértices (cada vértice é um padrão)
    g.add_vertices(validos)
    
    # Adiciona as arestas (conexões entre padrões)
    edges = []
    edge_labels = []
    
    # Itera apenas na metade superior da matriz para evitar duplicatas
    for i in range(len(validos)):
        #print(f"i: {i}")
        for j in range(i + 1, len(validos)):
            #print(f"    j: {j}")
            pecas_compartilhadas = matriz[validos[i], validos[j]]
            if pecas_compartilhadas:  # Se há peças compartilhadas
                #print(f"    encontrou peças compartilhadas entre {validos[i]} e {validos[j]}")
                edges.append((i, j))
                edge_labels.append(", ".join(map(str, pecas_compartilhadas)))
    
    g.add_edges(edges)
    
    # Configurações visuais
    visual_style = {
        "vertex_label": [ f"Padrão {i}\n{dominantes[i]}" if i in dominantes else f"Padrão {i}" for i in validos],
        "edge_label": edge_labels,
        "vertex_color": "lightblue",
        "edge_color": "gray",
        "vertex_size": 66,
        "layout": g.layout("fr"),  # Layout Fruchterman-Reingold
        "bbox": (1920, 1080),
        "margin": 50
    }
    
    # Plota o grafo
    plot(g, target=f"{nomeArq}.png", **visual_style)
