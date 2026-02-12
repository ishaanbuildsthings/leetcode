class Solution:
    def buildWall(self, height: int, width: int, bricks: List[int]) -> int:
        MOD = 10**9 + 7

        masks = Counter() # how many ways is each mask doable

        def bricksToMask(bricks):
            curr = 0
            mask = 0
            for v in bricks[:-1]:
                curr += v
                mask |= (1 << curr)
            return mask


        def bt(bricksHere, w):
            if w > width:
                return
            if w == width:
                masks[bricksToMask(bricksHere)] += 1
                return
            for brick in bricks:
                bricksHere.append(brick)
                bt(bricksHere, w + brick)
                bricksHere.pop()
        
        bt([], 0)

        adjMasks = defaultdict(list)
        for m1 in masks.keys():
            adjMasks[-1].append(m1)
            for m2 in masks.keys():
                if not m1 & m2:
                    adjMasks[m1].append(m2)
        
        @cache
        def dp(row, aboveLineMask):
            if row == height:
                return 1
            resHere = 0
            for adjMask in adjMasks[aboveLineMask]:
                resHere += dp(row + 1, adjMask) * masks[adjMask]
                resHere %= MOD
            return resHere
        
        return dp(0, -1)
            