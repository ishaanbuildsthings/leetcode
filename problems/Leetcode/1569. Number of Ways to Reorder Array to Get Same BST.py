class Node:
    def __init__(self, v):
        self.v = v
        self.l = None
        self.r = None

class Solution:
    def numOfWays(self, nums: list[int]) -> int:
        n = len(nums)
        rt = Node(nums[0])

        def insert(val):
            curr = rt
            node = Node(val)
            while True:
                if val < curr.v:
                    if not curr.l:
                        curr.l = node
                        break
                    else:
                        curr = curr.l
                else:
                    if not curr.r:
                        curr.r = node
                        break
                    else:
                        curr = curr.r
        
        for i in range(1, n):
            v = nums[i]
            insert(v)
        
        MOD = 10**9 + 7

        @cache
        def sz(node):
            if not node:
                return 0
            return 1 + sz(node.l) + sz(node.r)


        @cache
        def dp(node):
            if not node:
                return 1
            sizeL = sz(node.l)
            sizeR = sz(node.r)
            ways = comb(sizeL + sizeR, sizeL)
            ways = ways * dp(node.l) % MOD
            ways = ways * dp(node.r) % MOD
            return ways % MOD

        return (dp(rt) - 1) % MOD

        
        