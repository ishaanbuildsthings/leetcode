class Solution:
    def minMoves(self, classroom: List[str], energyI: int) -> int:
        height = len(classroom)
        width = len(classroom[0])
        lits = []
        o = []
        for r in range(height):
            for c in range(width):
                if classroom[r][c] == 'S':
                    start = (r, c)
                elif classroom[r][c] == 'L':
                    lits.append((r, c))
                elif classroom[r][c] == 'X':
                    o.append((r, c))
        if not lits:
            return 0
        litToIdx = {
            lit : i for i, lit in enumerate(lits)
        }

        # states is (r, c, energy, bitmask) # 20*20*2^10*50
        fullMask = (1 << len(lits)) - 1
        q = deque()
        q.append((start[0], start[1], energyI, 0))
        steps = 0
        seen = set()
        seen.add((start[0], start[1], energyI, 0))
        highestEnergies = defaultdict(lambda: -inf) # maps r, c, mask -> best energy
        while q:
            length = len(q)
            for _ in range(length):
                popped = q.popleft()
                r, c, energy, mask = popped
                if highestEnergies[(r, c, mask)] >= energy:
                    continue
                highestEnergies[(r, c, mask)] = energy
                if mask == fullMask:
                    return steps
                for rDiff, cDiff in [[1,0],[-1,0],[0,1],[0,-1]]:
                    nr, nc = r+rDiff, c + cDiff
                    if nr < 0 or nc < 0 or nr == height or nc == width:
                        continue
                    if classroom[nr][nc] == 'X':
                        continue
                    if energy == 0:
                        continue
                    newEnergy = energyI if classroom[nr][nc] == 'R' else energy - 1
                    if classroom[nr][nc] == 'L':
                        idx = litToIdx[(nr, nc)]
                        newMask = mask | (1 << idx)
                    else:
                        newMask = mask
                    newTup = (nr, nc, newEnergy, newMask)
                    if newTup in seen:
                        continue
                    seen.add(newTup)
                    q.append(newTup)
            steps += 1

        return -1
                    
                    
                    
                    