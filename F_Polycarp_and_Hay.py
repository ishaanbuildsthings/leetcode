n, m, k = map(int, input().split())
grid = []
for _ in range(n):
    row = list(map(int, input().split()))
    grid.append(row)

standard_input, packages, output_together = 1, 1, 0   # ← delete
dfs, hashing, read_from_file = 0, 0, 0     # ← delete
deb = 1                                     # ← delete
from math import inf                        # ← delete (or move to top)
# print(grid)

# TEMPLATE
# unions by depth

class DSU:
    def __init__(self, n):
        self.parents = list(range(n))
        self.sizes = [1] * n
        self.count = n

    def _find(self, x):
        root = x
        while self.parents[root] != root:
            root = self.parents[root]
        while self.parents[x] != root:
            self.parents[x], x = root, self.parents[x]
        return root

    def union(self, a, b):
        ra = self._find(a)
        rb = self._find(b)
        if ra == rb:
            return False
        if self.sizes[ra] < self.sizes[rb]:
            ra, rb = rb, ra
        self.parents[rb] = ra
        self.sizes[ra] += self.sizes[rb]
        self.count -= 1
        return True

    def areUnioned(self, a, b):
        return self._find(a) == self._find(b)

    def getSize(self, x):
        return self.sizes[self._find(x)]

    def uniqueComponents(self):
        return self.count
cells = []
for r in range(n):
    for c in range(m):
        cells.append((grid[r][c], r, c))

cells.sort(reverse=True)

nodes = []
for r in range(n):
    for c in range(m):
        nodes.append((r, c))
dsu = DSU(n * m)

found = None
active = [[False] * m for _ in range(n)]
for ht, r, c in cells:
    active[r][c] = True
    for rd, cd in [[1, 0], [-1, 0], [0, 1], [0, -1]]:
        nr, nc = r + rd, c + cd
        if nr < 0 or nr == n or nc < 0 or nc == m:
            continue
        if active[nr][nc]:
            dsu.union(r * m + c, nr * m + nc)
    if k % ht == 0 and dsu.getSize(r * m + c) >= k // ht:
        found = (ht, r, c)
        break

if not found:
    print('NO')
else:
    ht, sr, sc = found
    req = k // ht
    res = [[0] * m for _ in range(n)]
    cnt = 0

    stack = [(sr, sc)]
    while stack and cnt < req:
        r, c = stack.pop()
        if not (0 <= r < n and 0 <= c < m):
            continue
        if res[r][c] != 0 or grid[r][c] < ht:
            continue
        res[r][c] = ht
        cnt += 1
        stack.append((r + 1, c))
        stack.append((r - 1, c))
        stack.append((r, c + 1))
        stack.append((r, c - 1))

    print('YES')
    print('\n'.join(' '.join(map(str, row)) for row in res))