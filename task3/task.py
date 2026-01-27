import json
import ast


def ranking_to_matrix(ranking, all_elements):
    n = len(all_elements)
    matrix = [[0] * n for _ in range(n)]
    
    positions = {}
    pos = 0
    for item in ranking:
        if isinstance(item, list):
            for elem in item:
                positions[elem] = pos
            pos += 1
        else:
            positions[item] = pos
            pos += 1
    
    for i, elem_i in enumerate(all_elements):
        for j, elem_j in enumerate(all_elements):
            pos_i = positions.get(elem_i, float('inf'))
            pos_j = positions.get(elem_j, float('inf'))
            if pos_j <= pos_i:
                matrix[i][j] = 1
    
    return matrix


def logical_multiply(matrix_a, matrix_b):
    n = len(matrix_a)
    result = [[0] * n for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            if matrix_a[i][j] == 1 and matrix_b[i][j] == 1:
                result[i][j] = 1
    
    return result


def find_contradiction_core(matrix, all_elements):
    n = len(all_elements)
    contradictions = set()
    
    for i in range(n):
        for j in range(i + 1, n):
            if matrix[i][j] == 0 and matrix[j][i] == 0:
                contradictions.add(frozenset([all_elements[i], all_elements[j]]))
    
    clusters = []
    processed = set()
    
    for contradiction in contradictions:
        if contradiction in processed:
            continue
        
        cluster = set(contradiction)
        processed.add(contradiction)
        
        changed = True
        while changed:
            changed = False
            for other in contradictions:
                if other in processed:
                    continue
                if cluster & other:
                    cluster |= other
                    processed.add(other)
                    changed = True
        
        if len(cluster) > 1:
            clusters.append(sorted(list(cluster)))
    
    return sorted(clusters, key=lambda x: (len(x), x))


def build_consensus_ranking(matrix, all_elements, contradiction_core):
    n = len(all_elements)
    
    element_to_cluster = {}
    for cluster in contradiction_core:
        for elem in cluster:
            element_to_cluster[elem] = cluster
    
    better_than = {}
    for i in range(n):
        elem_i = all_elements[i]
        better_than[elem_i] = set()
        for j in range(n):
            if i != j:
                elem_j = all_elements[j]
                if matrix[i][j] == 1 and matrix[j][i] == 0:
                    better_than[elem_i].add(elem_j)
    
    remaining = set(all_elements)
    result = []
    processed = set()
    
    while remaining:
        current_level = []
        for elem in remaining:
            has_better = any(better in remaining for better in better_than.get(elem, set()))
            if not has_better:
                current_level.append(elem)
        
        level_clusters = {}
        level_singles = []
        
        for elem in current_level:
            if elem in element_to_cluster:
                cluster = element_to_cluster[elem]
                cluster_key = tuple(sorted(cluster))
                if all(e in current_level for e in cluster):
                    if cluster_key not in level_clusters:
                        level_clusters[cluster_key] = cluster
                elif elem not in processed:
                    level_singles.append(elem)
            else:
                level_singles.append(elem)
        
        for cluster in sorted(level_clusters.values(), key=lambda x: min(x)):
            if len(cluster) > 1:
                result.append(sorted(cluster))
            else:
                result.append(cluster[0])
            for elem in cluster:
                processed.add(elem)
                remaining.discard(elem)
        
        for elem in sorted(level_singles):
            if elem not in processed:
                result.append(elem)
                processed.add(elem)
                remaining.discard(elem)
    
    return result


def main(ranking_a_json, ranking_b_json):
    try:
        ranking_a = json.loads(ranking_a_json)
    except:
        ranking_a = ast.literal_eval(ranking_a_json)
    
    try:
        ranking_b = json.loads(ranking_b_json)
    except:
        ranking_b = ast.literal_eval(ranking_b_json)
    
    def extract_elements(ranking):
        elements = set()
        for item in ranking:
            if isinstance(item, list):
                elements.update(item)
            else:
                elements.add(item)
        return elements
    
    all_elements = sorted(list(extract_elements(ranking_a) | extract_elements(ranking_b)))
    
    matrix_a = ranking_to_matrix(ranking_a, all_elements)
    matrix_b = ranking_to_matrix(ranking_b, all_elements)
    consensus_matrix = logical_multiply(matrix_a, matrix_b)
    
    contradiction_core = find_contradiction_core(consensus_matrix, all_elements)
    consensus_ranking = build_consensus_ranking(consensus_matrix, all_elements, contradiction_core)
    
    return json.dumps(consensus_ranking, ensure_ascii=False)
