class Solution:
    def countCombinations(self, pieces: list[str], positions: list[list[int]]) -> int:

        def oob(r, c):
            return r < 1 or r >= 9 or c < 1 or c >= 9

        # gives 4 lists of [(r, c, time1), (r, c, time2), ...]
        def rookMoves(r, c):
            moves = [[],[],[],[]]
            diffs = [[1,0],[-1,0],[0,1],[0,-1]]
            for i in range(len(diffs)):
                rd, cd = diffs[i]
                for time in range(1, 9):
                    nr = r + (rd * time)
                    nc = c + (cd * time)
                    if oob(nr, nc):
                        continue
                    moves[i].append((nr, nc, time))
            return moves

        # gives 4 lists of [(r, c, time1), (r, c, time2), ...]
        def bishopMoves(r, c):
            moves = [[],[],[],[]]
            diffs = [[1,1],[-1,-1],[1,-1],[-1,1]]
            for i in range(len(diffs)):
                rd, cd = diffs[i]
                for time in range(1, 9):
                    nr = r + (rd * time)
                    nc = c + (cd * time)
                    if oob(nr, nc):
                        continue
                    moves[i].append((nr, nc, time))
            return moves
        
        # gives 8 lists of [(r, c, time1), (r, c, time2), ...]
        def queenMoves(r, c):
            return rookMoves(r, c) + bishopMoves(r, c)
        
        pieceLists = []
        for i in range(len(pieces)):
            piece = pieces[i]
            r, c = positions[i]
            lst = rookMoves(r, c) if piece == 'rook' else bishopMoves(r, c) if piece == 'bishop' else queenMoves(r, c)
            pieceLists.append(lst)
        
        res = 0
        
        def bt(pieceI, timeMovesSet):
            nonlocal res
            if pieceI == len(pieces):
                res += 1
                return

            # stay put
            r, c = positions[pieceI]
            if not any((r, c, t) in timeMovesSet for t in range(1, 9)):
                for t in range(1, 9):
                    timeMovesSet.add((r, c, t))
                bt(pieceI + 1, timeMovesSet)
                for t in range(1, 9):
                    timeMovesSet.remove((r, c, t))

            channels = pieceLists[pieceI]
            for channel in channels:
                for i in range(len(channel)):
                    pf = channel[:i+1]
                    finalR, finalC, finalTime = pf[-1]
                    arr = pf[:]
                    for time in range(finalTime + 1, 9):
                        arr.append((finalR, finalC, time))
                    s = set(arr)
                    if s & timeMovesSet:
                        continue
                    timeMovesSet |= s
                    bt(pieceI + 1, timeMovesSet)
                    for v in s:
                        timeMovesSet.remove(v)
        bt(0, set())
        return res


