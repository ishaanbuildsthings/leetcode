class Solution:
    def maxConsistentColumns(self, grid: List[List[int]], limit: int) -> int:

        height = len(grid)
        width = len(grid[0])



        # current column we are considering, previous column we kept (or None if not kept)

        # we can delete this column always

        # or we can keep it if valid
        @cache
        def dp(c, prevC):
            if c == width:
                return 0

            res = 0

            ifSkip = dp(c + 1, prevC)

            # can we take this?

            if prevC is None:
                ifTake = 1 + dp(c + 1, c)

                return max(ifSkip, ifTake)

            failFound = False

            for r in range(height):
                prev = grid[r][prevC]

                diff = abs(prev - grid[r][c])
                if diff > limit:
                    failFound = True
                    break

            if failFound:
                return ifSkip

            ifTake = 1 + dp(c + 1, c)

            return max(ifSkip, ifTake)

        ans = dp(0, None)
        dp.cache_clear()

        return ans

            
            