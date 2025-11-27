import math
import csv
from io import StringIO
from typing import Tuple

def task(s: str, e: str) -> Tuple[float, float]:
    edges = []
    nodes = set()
    
    reader = csv.reader(StringIO(s))
    for row in reader:
        if len(row) == 2:
            source, target = row[0].strip(), row[1].strip()
            edges.append((source, target))
            nodes.add(source)
            nodes.add(target)
    
    nodes.add(e)
    
    nodes = sorted(nodes, key=lambda x: int(x))
    n = len(nodes)
    node_to_index = {node: idx for idx, node in enumerate(nodes)}
        
    r1 = edges.copy()
    
    r2 = [(target, source) for source, target in edges]
    
    graph = {node: set() for node in nodes}
    for source, target in edges:
        graph[source].add(target)
    
    def get_all_descendants(node, visited=None):
        if visited is None:
            visited = set()
        descendants = set()
        for child in graph.get(node, set()):
            if child not in visited:
                visited.add(child)
                descendants.add(child)
                descendants |= get_all_descendants(child, visited)
        return descendants
    
    r3 = []
    for node in nodes:
        all_descendants = get_all_descendants(node)
        direct_descendants = set(graph.get(node, set()))
        indirect_descendants = all_descendants - direct_descendants
        for descendant in indirect_descendants:
            r3.append((node, descendant))
    
    r4 = [(target, source) for source, target in r3]
    
    parent_map = {}
    for source, target in edges:
        parent_map[target] = source
    
    r5 = []
    siblings = {}
    for node in nodes:
        if node in parent_map:
            parent = parent_map[node]
            if parent not in siblings:
                siblings[parent] = []
            siblings[parent].append(node)
    
    for parent, children in siblings.items():
        if len(children) > 1:
            for i in range(len(children)):
                for j in range(i + 1, len(children)):
                    r5.append((children[i], children[j]))
                    r5.append((children[j], children[i]))
    
    relations = [r1, r2, r3, r4, r5]
    relation_names = ['r1', 'r2', 'r3', 'r4', 'r5']
    
    lij_table = {node: {f'r{i+1}': 0 for i in range(5)} for node in nodes}
    
    for i, relation in enumerate(relations):
        relation_name = f'r{i+1}'
        for source, target in relation:
            if source in lij_table:
                lij_table[source][relation_name] += 1
    
    max_possible_links = n - 1
    total_entropy = 0.0
    
    for node in nodes:
        node_entropy = 0.0
        for relation_name in relation_names:
            lij = lij_table[node][relation_name]
            if lij > 0:
                P = lij / max_possible_links
                H = -P * math.log2(P)
                node_entropy += H
        total_entropy += node_entropy
    
    c = 1 / (math.e * math.log(2))  
    k = 5  
    H_ref = c * n * k
    
    h_normalized = total_entropy / H_ref
    
    return round(total_entropy, 1), round(h_normalized, 1)

if __name__ == "__main__":
    csv_string = "1,2\n1,3\n3,4\n3,5"
    root = "1"
    result = task(csv_string, root)
    print(f"Энтропия: {result[0]}, Нормированная сложность: {result[1]}")