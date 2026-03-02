class Solution:
    def maximumWhiteTiles(self, tiles: List[List[int]], carpetLen: int) -> int:
        tiles.sort()
        print(tiles)

        pf = []
        curr = 0
        for a, b in tiles:
            curr += b - a + 1
            pf.append(curr)
        
        def squery(l, r):
            if l > r: return 0
            return pf[r] - (pf[l - 1] if l else 0)

        res = 0
        l = r = 0
        covered = 0
        n = len(tiles)
        # claim, am optimal layout can always have the carpet ending at a time
        while r < n:
            start, end = tiles[r]
            # while the left is dropped off, do so
            while end - tiles[l][1] >= carpetLen:
                # lostStart, lostEnd = tiles[0]
                l += 1
            
            # handled this separately to avoid double counting it
            if l == r:
                inThisTile = min(end - start + 1, carpetLen)
                res = max(res, inThisTile)
                r += 1
                continue
            
            # now we are going from some ending left tile ... our r-th tile end
            inRightTile = min(carpetLen, end - start + 1)
            inBetween = squery(l + 1, r - 1)

            # we are always touching some left tile so this is always positive
            availForLeftTile = carpetLen - (end - tiles[l][1])
            inLeftTile = min(availForLeftTile, tiles[l][1] - tiles[l][0] + 1)
            gain = inRightTile + inBetween + inLeftTile
            res = max(res, gain)
            r += 1
        
        return res


                