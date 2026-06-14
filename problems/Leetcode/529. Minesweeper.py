class Solution:
    def updateBoard(self, board: List[List[str]], click: List[int]) -> List[List[str]]:
        height = len(board)
        width = len(board[0])

        clickR, clickC = click
        if board[clickR][clickC] == 'M':
            board[clickR][clickC] = 'X'
            return board
        
        def getAdjs(r, c):
            res = []
            for rDiff, cDiff in [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,-1],[-1,1]]:
                nr, nc = r + rDiff, c + cDiff
                if nr < 0 or nr == height or nc < 0 or nc == width:
                    continue
                res.append((nr, nc))
            return res
        
        seen = {(clickR, clickC)}

        def getCount(adjList):
            count = 0
            for r, c in adjList:
                count += board[r][c] == 'M'
            return count
        
        def dfs(r, c):
            seen.add((r, c))
            board[r][c] = 'B'
            adjs = getAdjs(r, c)
            adjCount = getCount(adjs)
            if adjCount:
                board[r][c] = str(adjCount)
                return
            for adj in adjs:
                if adj in seen:
                    continue
                dfs(adj[0], adj[1])

        dfs(clickR, clickC)

        return board
