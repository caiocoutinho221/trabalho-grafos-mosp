import time
from preprocessamento import checa_dominados, reducao_padroes_por_pseudo_equivalencia, pre_processamento_colapso_grau2
from grafo import Graph, SubGraph
import csv
import os
import sequenciamento

# Configurações de diretório
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(BASE_DIR, 'datasets', 'Frinhani, Carvalho & Soma')
RESULTADOS_DIR = os.path.join(BASE_DIR, 'resultados')
os.makedirs(RESULTADOS_DIR, exist_ok=True)

# Nome do arquivo de resultados com timestamp
timestamp = time.strftime("%Y%m%d_%H%M%S")
CSV_RESULTADOS = os.path.join(RESULTADOS_DIR, f'resultados_tamanho_{timestamp}.csv')

tecnicas_pre_processamento = {
    "sem": None,
    "p1": checa_dominados,
    "p2": reducao_padroes_por_pseudo_equivalencia,
    "p3": pre_processamento_colapso_grau2
}

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

def executar_experimentos_tamanho():
    # Cabeçalho do CSV
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
                # Ignorar arquivos de descrição e não-texto
                if file.startswith('Dataset_Description') or not file.endswith('.txt'):
                    continue
                
                # Obter caminho relativo no formato 'Challenge/GP1'
                relative_path = os.path.relpath(os.path.join(root, file), os.path.join(BASE_DIR, 'datasets'))
                instancia_relativa = os.path.splitext(relative_path)[0]  # Remove .txt
                
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
    executar_experimentos_tamanho()