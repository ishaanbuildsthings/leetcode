class Solution:
    def minimumCost(self, nums: list[int], k: int) -> int:

        MOD = 10**9 + 7

        cur = k # current resources

        nextCost = 1

        res = 0

        # sum of 1+2+...+n
        # first n
        def tri(n):
            return (n * (n + 1)) // 2
        

        for i, v in enumerate(nums):
            if cur >= v:
                cur -= v
                continue

            diff = v - cur

            ops = math.ceil(diff / k)

            lowCost = nextCost
            highCost = lowCost + ops - 1

            # sum of lowCost + lowCost+1 + ... + highCost

            up = tri(highCost)
            down = tri(lowCost - 1) if lowCost else 0

            cur += (k * ops)
            cur -= v

            nextCost = highCost + 1

            spend = up - down

            res += spend
            res %= MOD

        return res

            