class Solution:
    def calculateMinimumHP(self, dungeon: List[List[int]]) -> int:
        # Solution 1 with binary search on answer + dp, slower
        # height = len(dungeon)
        # width = len(dungeon[0])

        # def win(startHealth):
        #     maxHealths = [[-inf] * width for _ in range(height)]
        #     maxHealths[0][0] = startHealth + dungeon[0][0]
        #     if maxHealths[0][0] <= 0:
        #         return False
        #     for r in range(height):
        #         for c in range(width):
        #             if r == c == 0:
        #                 continue
        #             up = maxHealths[r - 1][c] if r else -inf
        #             left = maxHealths[r][c - 1] if c else -inf
        #             maxHealths[r][c] = max(up, left) + dungeon[r][c]
        #             if maxHealths[r][c] <= 0:
        #                 maxHealths[r][c] = -inf
        #     return maxHealths[-1][-1] > 0


        # res = inf
        # l = 1
        # r = 10**18
        # while l <= r:
        #     m = (r + l) // 2
        #     if win(m):
        #         res = m
        #         r = m - 1
        #     else:
        #         l = m + 1
        # return res

        # Solution 2 with straight dp
        height = len(dungeon)
        width = len(dungeon[0])
        # min needed health to survive from here to the end
        @cache
        def dp(r, c):
            if r == height - 1 and c == width - 1:
                if dungeon[r][c] < 0:
                    return abs(dungeon[r][c]) + 1
                return 1
            
            downNeed = dp(r + 1, c) if r + 1 < height else inf
            rightNeed = dp(r, c + 1) if c + 1 < width else inf

            # we only need 1 here
            if dungeon[r][c] >= 0:
                gained = dungeon[r][c] + 1
                withBestLoss = gained - min(downNeed, rightNeed)
                if withBestLoss >= 1:
                    return 1
                return 1 + abs(withBestLoss)

            if min(downNeed, rightNeed) > 1 + dungeon[r][c]:
                return min(downNeed, rightNeed) - dungeon[r][c]

                
            needHere = abs(dungeon[r][c]) + 1
            return max(needHere, min(downNeed, rightNeed))
        
        return dp(0, 0)
