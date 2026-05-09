class Solution:
    def minMoves(self, matrix: List[str]) -> int:
        q = deque()
        q.append((0,0,0)) # (r, c, moves)
        used = set() # portals we have used
        minDists = defaultdict(lambda : inf) # (r, c) -> min dist to reach that

        H = len(matrix)
        W = len(matrix[0])

        pos = defaultdict(list) # letter -> list (r, c)
        for r in range(H):
            for c in range(W):
                if matrix[r][c].isalpha():
                    pos[matrix[r][c]].append((r, c))

        while q:
            r, c, moves = q.popleft()
            if r == H - 1 and c == W - 1:
                return moves
            
            if minDists[(r, c)] <= moves:
                continue
            
            minDists[(r, c)] = moves
            
            # if we are a letter and can invoke the power, do it
            if matrix[r][c].isalpha() and matrix[r][c] not in used:
                used.add(matrix[r][c])
                for nr, nc in pos[matrix[r][c]]:
                    if moves < minDists[(nr, nc)]:
                        q.appendleft((nr, nc, moves))
            
            for rdiff, cdiff in [[1,0],[-1,0],[0,1],[0,-1]]:
                nr = r + rdiff
                nc = c + cdiff
                if (nr == H or nr < 0 or nc == W or nc < 0):
                    continue
                if matrix[nr][nc] == '#':
                    continue
                if moves + 1 < minDists[(nr, nc)]:
                    q.append((nr, nc, moves + 1))
        
        return -1



            