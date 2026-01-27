import numpy as np

def parse(s: str) -> dict:
    if s[0] == '[' and s[-1] == ']':
        s = s[1:-1].strip()
    pos_map = {}
    pos = 0
    i = 0
    n = len(s)

    while i < n:
        if s[i] == '[':
            j = s.find(']', i)
            if j == -1:
                raise ValueError("Нет ']'")
            content = s[i+1:j]
            items = [x.strip() for x in content.split(',') if x.strip()]
            for item in items:
                pos_map[item] = pos
            pos += 1
            i = j + 1
        elif s[i] == ',' or s[i].isspace():
            i += 1
        else:
            start = i
            while i < n and s[i] not in ',[':
                i += 1
            item = s[start:i].strip()
            if item:
                pos_map[item] = pos
                pos += 1
    return pos_map


def make_matrix(pos_map, items):
    n = len(items)
    mat = np.zeros((n, n), bool)
    for i1 in range(n):
        pos1 = pos_map[items[i1]]
        for i2 in range(n):
            pos2 = pos_map[items[i2]]
            if pos1 <= pos2:
                mat[i1][i2] = 1
    return mat


def main(str1: str, str2: str):
    items = [x.strip(',[]') for x in str1.split(',')]

    map1 = parse(str1)
    map2 = parse(str2)
    mat1 = make_matrix(map1, items)
    mat2 = make_matrix(map2, items)

    mat1T = mat1.T
    mat2T = mat2.T

    mat12 = mat1 * mat2
    mat12T = mat1T * mat2T
    mat_dis = mat12 + mat12T

    bad_pos = list(zip(*np.where(~mat_dis)))
    pairs_set = {tuple(sorted(p)) for p in bad_pos}
    contradictions = [(items[i], items[j]) for i, j in pairs_set]

    matC = mat12.copy()

    for x, y in contradictions:
        idx1 = items.index(x)
        idx2 = items.index(y)
        matC[idx1, idx2] = 1
        matC[idx2, idx1] = 1
    matE = matC * matC.T
    n_items = len(items)
    matE_star = matE.copy()
    for k in range(n_items):
        for i in range(n_items):
            for j in range(n_items):
                matE_star[i, j] = matE_star[i, j] or (matE_star[i, k] and matE_star[k, j])

    visited = [False] * n_items
    clusters = []
    for i in range(n_items):
        if not visited[i]:
            cluster = []
            for j in range(n_items):
                if matE_star[i, j]:
                    cluster.append(items[j])
                    visited[j] = True
            clusters.append(cluster)

    def compare(c1, c2):
        for a in c1:
            idx_a = items.index(a)
            for b in c2:
                idx_b = items.index(b)
                if matC[idx_a, idx_b] == 0:
                    return False
        return True

    changed = True
    while changed:
        changed = False
        for i in range(len(clusters) - 1):
            if compare(clusters[i+1], clusters[i]):
                clusters[i], clusters[i+1] = clusters[i+1], clusters[i]
                changed = True

    result = []
    for cluster in clusters:
        if len(cluster) == 1:
            result.append(cluster[0])
        else:
            result.append(cluster)

    return result


str1 = '[1,[2,3],4,[5,6,7],8,9,10]'
str2 = '[[1,2],[3,4,5],6,7,9,[8,10]]'
print(main(str1, str2))

str3 = "[x1,[x2,x3],x4,[x5,x6,x7],x8,x9,x10]"
str4 = "[x3,[x1,x4],x2,x6,[x5,x7,x8],[x9,x10]]"
# print(main(str3, str4))

str5 = '[T,[K,M],D,Z]'
str6 = '[[T,K],M,Z,D]'
# print(main(str5, str6))
