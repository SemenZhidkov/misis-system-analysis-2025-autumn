import json
import numpy as np
from itertools import combinations

def flatten_ranking(ranking):
    """Разворачивает кластерную ранжировку в плоский список объектов"""
    objects = []
    for item in ranking:
        if isinstance(item, list):
            objects.extend(item)
        else:
            objects.append(item)
    return sorted(objects)

def ranking_to_matrix(ranking, objects):
    """Преобразует ранжировку в матрицу отношений"""
    n = len(objects)
    matrix = np.zeros((n, n), dtype=int)
    
    positions = {}
    pos = 0
    for cluster in ranking:
        cluster_list = cluster if isinstance(cluster, list) else [cluster]
        for obj in cluster_list:
            positions[obj] = pos
        pos += 1
    
    for i, obj_i in enumerate(objects):
        for j, obj_j in enumerate(objects):
            if positions[obj_i] <= positions[obj_j]:
                matrix[i][j] = 1
    return matrix

def find_core_and_consistent_ranking(ranking_a_str, ranking_b_str):
    """Основная функция для нахождения ядра противоречий и согласованной ранжировки"""
    
    ranking_a = json.loads(ranking_a_str)
    ranking_b = json.loads(ranking_b_str)
    
    objects = flatten_ranking(ranking_a)
    
    Y_A = ranking_to_matrix(ranking_a, objects)
    Y_B = ranking_to_matrix(ranking_b, objects)
    
    Y_A_T = Y_A.T
    Y_B_T = Y_B.T
    
    P = (Y_A & Y_B_T) | (Y_A_T & Y_B)
    
    core = []
    n = len(objects)
    for i in range(n):
        for j in range(i + 1, n):
            if P[i][j] == 0:
                core.append([objects[i], objects[j]])
    
    C = Y_A & Y_B
    
    for pair in core:
        i = objects.index(pair[0])
        j = objects.index(pair[1])
        C[i][j] = C[j][i] = 1
    
    E = C & C.T
    
    E_star = E.copy()
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if E_star[i][k] and E_star[k][j]:
                    E_star[i][j] = 1
    
    clusters = []
    visited = [False] * n
    
    for i in range(n):
        if not visited[i]:
            cluster = []
            stack = [i]
            visited[i] = True
            
            while stack:
                node = stack.pop()
                cluster.append(objects[node])
                for j in range(n):
                    if E_star[node][j] and not visited[j]:
                        visited[j] = True
                        stack.append(j)
            
            clusters.append(sorted(cluster))
    
    def get_cluster_position(cluster, ranking):
        """Находит позицию кластера в ранжировке"""
        for pos, item in enumerate(ranking):
            item_list = item if isinstance(item, list) else [item]
            if any(obj in item_list for obj in cluster):
                return pos
        return len(ranking)
    
    clusters.sort(key=lambda cluster: 
                 (get_cluster_position(cluster, ranking_a) + 
                  get_cluster_position(cluster, ranking_b)) / 2)
    
    consistent_ranking = []
    for cluster in clusters:
        if len(cluster) == 1:
            consistent_ranking.append(cluster[0])
        else:
            consistent_ranking.append(cluster)
    
    return {
        "core": core,
        "consistent_ranking": consistent_ranking
    }

if __name__ == "__main__":
    ranking_a = '[1,[2,3],4,[5,6,7],8,9,10]'
    ranking_b = '[[1,2],[3,4,5],6,7,9,[8,10]]'
    
    result = find_core_and_consistent_ranking(ranking_a, ranking_b)
    
    print("Ядро противоречий:")
    print(json.dumps(result["core"], ensure_ascii=False))
    
    print("\nСогласованная кластерная ранжировка:")
    print(json.dumps(result["consistent_ranking"], ensure_ascii=False))