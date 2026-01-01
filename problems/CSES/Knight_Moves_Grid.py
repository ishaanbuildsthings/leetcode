import collections, sys
n = int(input())
q = collections.deque()
q.append((0, 0))
steps = 0
out = [
    [
        -1 for _ in range(n)
    ] for _ in range(n)
]
out[0][0] = 0
while q:
    length = len(q)
    for _ in range(length):
        r, c = q.popleft()
        for rDiff, cDiff in [[1,2],[-1,2],[1,-2],[-1,-2],[2,1],[2,-1],[-2,1],[-2,-1]]:
            nr = r + rDiff
            nc = c + cDiff
            if nr < 0 or nr >= n or nc < 0 or nc >= n or out[nr][nc] != -1:
                continue
            out[nr][nc] = steps + 1
            q.append((nr, nc))
    steps += 1

out = "\n".join(" ".join(map(str, row)) for row in out)
sys.stdout.write(out)