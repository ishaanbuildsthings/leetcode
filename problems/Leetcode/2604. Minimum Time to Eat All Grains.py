class Solution:
    def minimumTime(self, hens: List[int], grains: List[int]) -> int:
        grains.sort()
        hens.sort()
        G = len(grains)

        # can all hens collect all grains in X time?
        def canDo(X):
            # j is the rightmost grain we still need to reach
            j = 0
            for h in hens:
                # we finished all grains
                if j >= G:
                    return True
                # we can either go left then right or right then left
                if grains[j] <= h:
                    left = h - grains[j]
                    if left > X:
                        return False
                    reach1 = grains[j] + (X - left)
                    reach2 = h + (X - left) // 2
                    reach = max(reach1, reach2)
                else:
                    # if grain is on the right, we just go there
                    reach = h + X
                while j < G and grains[j] <= reach:
                    j += 1
            return j >= G

        l = 0
        r = 10**18
        res = None
        while l <= r:
            m = (l + r) // 2
            if canDo(m):
                res = m
                r = m - 1
            else:
                l = m + 1

        return res