# Sequenciamento e aplicação de técnicas de Pré-Processamento em Grafos no contexto do MOSP

Projeto desenvolvido para a disciplina **CMAC03 – Algoritmos em Grafos** (1º semestre de 2025 – UNIFEI), com foco no sequenciamento de padrões em problemas de corte e empacotamento, aplicando técnicas de grafos para minimizar o número de pilhas abertas.

---

## Contexto

Nos processos industriais de corte, a ordem dos padrões influencia diretamente no número de pilhas simultaneamente abertas (pilhas de peças). Minimizar esse número é importante para reduzir custo, espaço e tempo de operação. Neste projeto:

- Cada padrão é modelado como um vértice.
- Padrões que compartilham peças possuem arestas entre si.
- Pré-processamentos reduzem ou simplificam o grafo.
- Uma heurística de sequenciamento (Yuen3PPAD) é aplicada após o pré-processamento.

---

## Objetivos

- Reduzir a complexidade do grafo via pré-processamento.
- Gerar sequências de padrões com menor **NMPA** e **MMOSP**.
- Avaliar desempenho de diferentes técnicas em tempo e qualidade da solução.

---

## Técnicas de Pré-Processamento
 - p1 – Dominância

- p2 – Agrupamento por Pseudo Equivalência

- p3 – Colapso de Vértices de Grau 2

- sem: sequenciamento sem aplicação de pré-processamento

---
## Métricas Avaliadas

| Métrica             | Descrição                                                                                   |
|---------------------|---------------------------------------------------------------------------------------------|
| **NMPA**            | Número Máximo de Pilhas Abertas                                                             |
| **MMOSP**           | Modified MOSP                                                                               |
| **Gap (%)**         | Diferença percentual entre o NMPA obtido e o valor ótimo conhecido                          |
| **Gap seq (%)**     | Diferença percentual do MMOSP entre o sequenciamento sem técnica e com a técnica aplicada   |
| **Tempo (s)**       | Tempo total de execução (pré-processamento + sequenciamento)                                |
| **Densidade**       | Densidade do grafo após a execução das operações de pré-processamento                       |

---

## Estrutura do Projeto

```plaintext

│── grafo.py                     # Modelagem do grafo
│── preprocessamento.py          # Pré-processamentos (dominância, agrupamento, colapso)
│── sequenciamento.py            # Heurística Yuen3PPAD e métricas
│── testes.py                    # Execução de experimentos e geração de resultados
├── datasets/                        # Instâncias de entrada (.txt)
│   └── Faggioli_Bentivoglio/
│   └── Chu_Stuckey/
│   └── Frinhani, Carvalho & Soma/
│   └── SCOOP/
│   └── Challenge/
│   └── S1. Dataset - README FIRST.pdf
│         
├── valores_otimos/                 # Arquivos CSV com valores ótimos conhecidos
├── resultados/                     # Resultados gerados (.csv)
├── requirements.txt                # Dependências
└── README.md                       
```
---

## Como executar os testes

1 - Instale as dependências do projeto:
```bash
pip install -r requirements.txt
```
2. Execute o script de testes para rodar os experimentos:

```bash
python testes.py
```


