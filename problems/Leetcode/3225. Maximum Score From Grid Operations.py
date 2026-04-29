class Solution:
    def maximumScore(self, grid: List[List[int]]) -> int:

        # XXX
        # XXX
        # XXX
        # X X
        # X X # dont know if this gives us a point or not
        # X

        n = len(grid)

        # for a given column, finds the sum of all cells from 0...rowI
        @cache
        def tot(colI, rowI):
            if rowI == n:
                return 0
            return grid[rowI][colI] + tot(colI, rowI + 1)
        
        # range query for a vertical region of a column
        def vertQuery(col, r1, r2):
            suff1 = tot(col, r1)
            if r2 == n - 1:
                return suff1
            suff2 = tot(col, r2 + 1)
            return suff1 - suff2
        
        
        withScore = [0] * (n + 1) # dp for if we scored the last column, and dp[r] means r rows are painted
        withoutScore = [0] * (n + 1)

        # we can start at column 1, and initialize the above two dp arrays to all 0s, because we can't score with just the 0th column
        for c in range(1, n):
            nwithScore = [0] * (n + 1)
            nwithoutScore = [0] * (n + 1)
            for newPainted in range(n + 1):
                for prevPainted in range(n + 1):
                    # how much cell sums do we gain from previous being taller than the new block
                    newColScore = vertQuery(c, newPainted, prevPainted - 1) if prevPainted > newPainted else 0
                    # how much cell sums do we gain in the prior column from the new one being taller
                    prevColScore = vertQuery(c - 1, prevPainted, newPainted - 1) if newPainted > prevPainted else 0

                    # our new unscored could just be the previous one scored
                    nwithoutScore[newPainted] = max(nwithoutScore[newPainted], withScore[prevPainted])

                    # our new unscored could also be the previous unscored but now we are scoring that previous one with the current column
                    # not worried about "what if the previous column should've gotten scored from ITS previous column?"
                    # because this is handled by the fact that we update withScore states too
                    nwithoutScore[newPainted] = max(nwithoutScore[newPainted], withoutScore[prevPainted] + prevColScore)

                    # new scored could be the previous scored + how much we get from the previous being taller
                    nwithScore[newPainted] = max(nwithScore[newPainted], withScore[prevPainted] + newColScore)
                    
                    # # new scored could also be how much we got from the previous one being unscored, we score the previous one now with the current column, and the current column with the previous one
                    nwithScore[newPainted] = max(nwithScore[newPainted], withoutScore[prevPainted] + prevColScore + newColScore)
                    
            withScore = nwithScore
            withoutScore = nwithoutScore
        
        return max(withScore)

                