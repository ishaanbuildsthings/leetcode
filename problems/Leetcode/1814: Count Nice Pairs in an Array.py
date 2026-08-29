class Solution:
    def countNicePairs(self, nums: List[int]) -> int:
        revToCt = defaultdict(int)
        for n in nums:
            rev = int(str(n)[::-1])
            diff = n - rev
            revToCt[diff] += 1

        res = 0
        for n in nums:
            rev = int(str(n)[::-1])
            reqOffset = n - rev
            res += revToCt[reqOffset] - 1
        
        return (res // 2) % (10**9 + 7)