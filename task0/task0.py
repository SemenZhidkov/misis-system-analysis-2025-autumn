import pandas as pd 
import numpy as np

def edges_to_adjacency_matrix(edges_csv):
    edges = pd.read_csv(edges_csv, header=None, names=['from', 'to'])
    nodes = sorted(set(edges['from']).union(edges['to']))
    node_index = {node: i for i, node in enumerate(nodes)}

    size = len(nodes)
    adjacency_matrix = np.zeros((size, size), dtype=int)

    for _, row in edges.iterrows():
        from_idx = node_index[row['from']]
        to_idx = node_index[row['to']]
        adjacency_matrix[from_idx, to_idx] = 1
        adjacency_matrix[to_idx, from_idx] = 1

    return adjacency_matrix

def main(): 
    csv_path = 'task0/task2.csv'
    adjacency_matrix = edges_to_adjacency_matrix(csv_path)
    print("Матрица смежности:")
    print(adjacency_matrix)

main()