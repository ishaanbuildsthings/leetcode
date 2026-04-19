class Solution:
    def colorGrid(self, n: int, m: int, sources: list[list[int]]) -> list[list[int]]:
        h = n
        w = m
        colors = [[0] * w for _ in range(h) ]
        # print(colors)
        for r, c, col in sources:
            colors[r][c] = col

        # print(colors)

        seen = {(r, c) for (r, c, _) in sources}
        # print(seen)
        q = deque()
        for r, c, _ in sources:
            q.append((r, c))

        while q:
            # print(f'current colors: {colors}')
            length = len(q)
            lseen = set()
            for _ in range(length):
                r, c = q.popleft()
                for dr, dc in [[1,0],[-1,0],[0,1],[0,-1]]:
                    nr = r + dr
                    nc = c + dc
                    if nr >= h or nr < 0 or nc >= w or nc < 0:
                        continue
                    if (nr, nc) in seen:
                        continue
                    if (nr,nc) not in lseen:
                        q.append((nr, nc))
                    lseen.add((nr,nc))
                    colors[nr][nc] = max(colors[nr][nc], colors[r][c])
            seen |= lseen
        return colors
                    