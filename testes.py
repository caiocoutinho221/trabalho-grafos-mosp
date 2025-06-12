import time
from preprocessamento import checa_dominados, reducao_padroes_por_pseudo_equivalencia, pre_processamento_colapso_grau2
from grafo import Graph, SubGraph
import csv
import os
from sequenciamento import executaYuenPreProcessado, yuen3ppad, MMOSP, NMPA

# Configurações de diretório
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(BASE_DIR, 'datasets', 'Frinhani, Carvalho & Soma')
VALOR_OTIMO_DIR = os.path.join(BASE_DIR, 'valores_otimos')
RESULTADOS_DIR = os.path.join(BASE_DIR, 'resultados')
os.makedirs(RESULTADOS_DIR, exist_ok=True)

# Nome do arquivo de resultados com timestamp
timestamp = time.strftime("%Y%m%d_%H%M%S")
CSV_RESULTADOS = os.path.join(RESULTADOS_DIR, f'resultados_tamanho_{timestamp}.csv')
CSV_RESULTADOS_SEQ = os.path.join(RESULTADOS_DIR, f'resultados_sequenciamento_{timestamp}.csv')

tecnicas_pre_processamento = {
    "sem": None,
    "p1": checa_dominados,
    "p2": reducao_padroes_por_pseudo_equivalencia,
    "p3": pre_processamento_colapso_grau2
}

# Carregar valores ótimos dos arquivos
def carregar_valores_otimos():
    valores_otimos = {}
    
    # Carregar optsemmedia.csv
    caminho_optsemmedia = os.path.join(VALOR_OTIMO_DIR, 'optsemmedia.csv')
    if os.path.exists(caminho_optsemmedia):
        with open(caminho_optsemmedia, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Pular cabeçalho
            for row in reader:
                if len(row) >= 2:
                    dataset = row[0].strip()
                    try:
                        valores_otimos[dataset] = int(row[1])
                    except ValueError:
                        continue
    
    # Carregar optcommedia.csv
    caminho_optcommedia = os.path.join(VALOR_OTIMO_DIR, 'optcommedia.csv')
    if os.path.exists(caminho_optcommedia):
        with open(caminho_optcommedia, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Pular cabeçalho
            for row in reader:
                if len(row) >= 2:
                    dataset = row[0].strip()
                    try:
                        valores_otimos[dataset] = float(row[1])
                    except ValueError:
                        continue
    print(valores_otimos)
    return valores_otimos

# Dicionário global de valores ótimos
VALORES_OTIMOS = carregar_valores_otimos()

def run_timed_function(func, *args, **kwargs):
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()
    return end_time - start_time, result

def processar_instancia_sem_sequenciar(instancia_relativa, tecnica=None):
    grafo = Graph(instancia_relativa)
    vert, arest = grafo.contarVerticesArestas()
    dens = grafo.obtemDensidade()
    
    tempo_preprocess = 0.0
    if tecnica:
        tempo_preprocess, _ = run_timed_function(tecnica, grafo)
        vert, arest = grafo.contarVerticesArestas()
        dens = grafo.obtemDensidade()
    
    return {
        'tempo': tempo_preprocess,
        'tamanho': f"({vert};{arest})",
        'densidade': dens
    }
    
def processar_instancia_sequenciando(instancia_relativa, tecnica=None):
    grafo = Graph(instancia_relativa)
    
    dens = grafo.obtemDensidade()
    
    tempo_preprocess = 0.0
    tempo_seq = 0.0
    sol_mmosp = 0.0
    sol_nmpa = 0
    gap = 0
    sequencia_final = []
    
    if tecnica:
        tempo_preprocess, _ = run_timed_function(tecnica, grafo)
        tempo_seq, sequencia_final = run_timed_function(executaYuenPreProcessado, grafo)
    else:
        tempo_seq, sequencia_final = run_timed_function(yuen3ppad, grafo)
    
    sol_nmpa = NMPA(sequencia_final, grafo)
    sol_mmosp = MMOSP(sequencia_final, grafo)
    
    # Calcular gap usando os valores ótimos
    nome_dataset = os.path.basename(instancia_relativa)
    valor_otimo = VALORES_OTIMOS.get(nome_dataset)
    
    print(f"Valor otimo para {nome_dataset} é {valor_otimo}")
    
    if valor_otimo is not None and valor_otimo > 0:
        gap = ((sol_nmpa - valor_otimo) / valor_otimo) * 100
    
    return {
        'valorOtimo': valor_otimo,
        'tempo_total': tempo_preprocess + tempo_seq,
        'sol_nmpa': sol_nmpa,
        'sol_mmosp': sol_mmosp,
        'densidade': dens,
        'tempo_seq': tempo_seq,
        'gap': gap
    }

def executar_experimentos_sequenciamento():
    # Cabeçalho do CSV
    cabecalho = ['instancia', 'valorOtimo']
    for tecnica in tecnicas_pre_processamento.keys():
        cabecalho.extend([
            f'{tecnica}_tempo_total',
            f'{tecnica}_sol_nmpa',
            f'{tecnica}_sol_mmosp',
            f'{tecnica}_densidade',
            f'{tecnica}_tempo_seq',
            f'{tecnica}_gap',    
        ])
    
    with open(CSV_RESULTADOS_SEQ, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(cabecalho)
        
        for root, _, files in os.walk(DATASETS_DIR):
            for file in files:
                if file.startswith('Dataset_Description') or not file.endswith('.txt'):
                    continue
                
                relative_path = os.path.relpath(os.path.join(root, file), os.path.join(BASE_DIR, 'datasets'))
                instancia_relativa = os.path.splitext(relative_path)[0]
                
                print(f"\nProcessando instância: {instancia_relativa}")
                
                linha_resultados = [instancia_relativa]
                
                for nome_tecnica, funcao_tecnica in tecnicas_pre_processamento.items():
                    print(f"  - Técnica: {nome_tecnica}", end='', flush=True)
                    
                    resultados = processar_instancia_sequenciando(
                        instancia_relativa, 
                        funcao_tecnica if nome_tecnica != 'sem' else None
                    )
                    if nome_tecnica == 'sem':
                        linha_resultados.extend([resultados['valorOtimo']])
                        
                    linha_resultados.extend([
                        f"{resultados['tempo_total']:.3f}",
                        resultados['sol_nmpa'],
                        f"{resultados['sol_mmosp']:.3f}",
                        f"{resultados['densidade']:.3f}",
                        f"{resultados['tempo_seq']:.3f}",
                        f"{resultados['gap']:.2f}%"
                    ])
                    
                    print(f" | Tempo total: {resultados['tempo_total']:.3f}s | Gap: {resultados['gap']:.2f}%")
                
                writer.writerow(linha_resultados)
    
    print(f"\nExperimento de sequenciamento concluído! Resultados salvos em: {CSV_RESULTADOS_SEQ}")

def executar_experimentos_tamanho():
    cabecalho = ['instancia']
    for tecnica in tecnicas_pre_processamento.keys():
        cabecalho.extend([
            f'{tecnica}_tempo',
            f'{tecnica}_tamanho',
            f'{tecnica}_densidade'
        ])
    
    with open(CSV_RESULTADOS, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(cabecalho)
        
        for root, _, files in os.walk(DATASETS_DIR):
            for file in files:
                if file.startswith('Dataset_Description') or not file.endswith('.txt'):
                    continue
                
                relative_path = os.path.relpath(os.path.join(root, file), os.path.join(BASE_DIR, 'datasets'))
                instancia_relativa = os.path.splitext(relative_path)[0]
                
                print(f"\nProcessando instância: {instancia_relativa}")
                
                linha_resultados = [instancia_relativa]
                
                for nome_tecnica, funcao_tecnica in tecnicas_pre_processamento.items():
                    print(f"  - Técnica: {nome_tecnica}", end='', flush=True)
                    
                    resultados = processar_instancia_sem_sequenciar(
                        instancia_relativa, 
                        funcao_tecnica if nome_tecnica != 'sem' else None
                    )
                    
                    linha_resultados.extend([
                        f"{resultados['tempo']:.3f}",
                        resultados['tamanho'],
                        resultados['densidade']
                    ])
                    
                    print(f" | Tempo: {resultados['tempo']:.3f}s")
                
                writer.writerow(linha_resultados)
    
    print(f"\nExperimento concluído! Resultados salvos em: {CSV_RESULTADOS}")

if __name__ == "__main__":
   # executar_experimentos_tamanho()
    executar_experimentos_sequenciamento()