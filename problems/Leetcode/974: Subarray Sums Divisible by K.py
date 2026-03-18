class Solution:
    def subarraysDivByK(self, nums: List[int], k: int) -> int:
        count = defaultdict(int)
        count[0] = 1
        currSum = 0
        res = 0
        for v in nums:
            currSum += v
            reqCut = currSum % k
            res += count[reqCut]
            count[currSum % k] += 1
        return res
