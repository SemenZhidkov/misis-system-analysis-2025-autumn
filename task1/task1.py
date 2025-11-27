import csv
from collections import defaultdict, deque
from typing import List, Tuple, Dict
import numpy as np

'''
Задание 1. Для лабораторной работы по системному анализу: 

На входе список ребер в csv E и er-идентификатор корня дерева (может быть любым),
на выходе кортеж из 6 элементов-матриц: 1 матрица смежностей и 
5 матриц инцидентов r1-r5 (управления, транспонированная для него подчинения, 
опосредованного управления и транспонированная для него опосредованного подчинения и соподчинения)

'''



def read_edges_from_csv(filename: str) -> List[Tuple[str, str]]:
    """
    Читает ребра из CSV-файла. Каждая строка должна содержать минимум два значения
    (источник, цель).

    Возвращает список пар (u, v) в виде строк.
    """
    edges: List[Tuple[str, str]] = []
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # Пропускаем пустые строки и строки с менее чем 2 столбцами
            if not row or len(row) < 2:
                continue
            u, v = row[0].strip(), row[1].strip()
            # Пропускаем строки с пустыми значениями узлов
            if u == '' or v == '':
                continue
            edges.append((u, v))
    return edges


def build_tree(edges: List[Tuple[str, str]], root: str) -> Tuple[Dict[str, List[str]], List[str]]:
    """
    Строит ориентированное дерево (родитель -> дети) из неориентированного списка ребер
    с помощью обхода в ширину (BFS), начиная с узла `root`.

    Возвращает:
      - tree: словарь parent -> список children
      - nodes: упорядоченный список всех узлов (root первым, остальные — в отсортированном порядке)
    """
    # Сначала строим неориентированный список смежности
    undirected = defaultdict(list)
    all_nodes = set()
    for u, v in edges:
        undirected[u].append(v)
        undirected[v].append(u)
        all_nodes.update([u, v])

    if root not in all_nodes:
        raise ValueError(f"Root '{root}' not found among nodes: {sorted(all_nodes)}")

    # Обход в ширину (BFS) для ориентации ребер от корня (parent -> children)
    tree: Dict[str, List[str]] = defaultdict(list)
    visited = {root}
    q = deque([root])
    while q:
        parent = q.popleft()
        for neighbor in undirected[parent]:
            if neighbor not in visited:
                visited.add(neighbor)
                tree[parent].append(neighbor)
                q.append(neighbor)
    # Обеспечиваем стабильный порядок узлов: сначала root, затем остальные в отсортированном порядке
    others = sorted(n for n in all_nodes if n != root)
    nodes = [root] + others
    return tree, nodes


def build_matrices(tree: Dict[str, List[str]], nodes: List[str]) -> Tuple[np.ndarray, ...]:
    """
    По заданному ориентированному дереву (parent -> children) и упорядоченному списку узлов
    строит 6 матриц и возвращает их кортежом:

    (A, r1, r2, r3, r4, r5)

    Обозначения:
      - A: матрица смежности, A[i,j] = 1 если i -> j (родитель -> ребенок)
      - r1: матрица управления (то же, что A)
      - r2: транспонированная r1 (матрица подчинения)
      - r3: опосредованное управление: r3[i,j] = 1 если j — потомок i (на любом расстоянии >0)
      - r4: транспонированная r3 (опосредованное подчинение)
      - r5: соподчинение: r5[i,j] = 1 если i и j имеют общего родителя (братья/сестры), симметрична
    """
    n = len(nodes)
    idx = {node: i for i, node in enumerate(nodes)}

    # 1) Построить матрицу смежности A (parent -> child)
    A = np.zeros((n, n), dtype=int)
    for parent, children in tree.items():
        for child in children:
            A[idx[parent], idx[child]] = 1

    # 2) r1 — матрица управления (прямое управление)
    r1 = A.copy()

    # 3) r2 — транспонированная r1 (прямое подчинение)
    r2 = r1.T.copy()

    # 4) r3: опосредованное управление — достижимость (i -> j по направленным ребрам)
    r3 = np.zeros((n, n), dtype=int)
    # Для каждого узла выполняем DFS/BFS, чтобы пометить всех потомков
    for node in nodes:
        start = node
        if start not in tree and all(start not in children for children in tree.values()):
            # лист без детей -> потомков нет
            continue
        stack = list(tree.get(start, []))
        while stack:
            child = stack.pop()
            r3[idx[start], idx[child]] = 1
            # добавляем детей текущего ребенка (внуки и далее)
            stack.extend(tree.get(child, []))

    # 5) r4 — транспонированная r3 (опосредованное подчинение)
    r4 = r3.T.copy()

    # 6) r5: соподчинение (братья/сестры) — симметричная матрица
    r5 = np.zeros((n, n), dtype=int)
    for parent, children in tree.items():
        for i in range(len(children)):
            for j in range(i + 1, len(children)):
                a = idx[children[i]]
                b = idx[children[j]]
                r5[a, b] = 1
                r5[b, a] = 1

    return A, r1, r2, r3, r4, r5


def main(filename: str, root: str) -> Tuple[np.ndarray, ...]:
    """Верхнеуровневая функция: читает ребра из CSV, строит дерево от root, возвращает 6 матриц."""
    edges = read_edges_from_csv(filename)
    tree, nodes = build_tree(edges, root)
    matrices = build_matrices(tree, nodes)
    return matrices


if __name__ == '__main__':
    # Демо: при запуске как скрипт создаём небольшой CSV и печатаем матрицы
    demo_csv = 'example.csv'
    demo_edges = [
        ('root', 'A'),
        ('root', 'B'),
        ('A', 'A1'),
        ('A', 'A2'),
        ('B', 'B1'),
        ('B', 'B2'),
    ]
    # write demo file
    with open(demo_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for u, v in demo_edges:
            writer.writerow([u, v])

    mats = main(demo_csv, 'root')
    names = ['A', 'r1', 'r2', 'r3', 'r4', 'r5']
    for name, m in zip(names, mats):
        print(f"Matrix {name} (shape {m.shape}):\n{m}\n")