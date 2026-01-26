class Solution:
    def rotateElements(self, nums: List[int], k: int) -> List[int]:
        nonneg = deque([x for x in nums if x >= 0])
        if not nonneg:
            return nums
        k = k % len(nonneg)
        for _ in range(k):
            z=nonneg.popleft()
            nonneg.append(z)

        res = [None] * len(nums)
        for i, v in enumerate(nums):
            if v < 0:
                res[i] = v

        j = 0
        for i in range(len(res)):
            if res[i] is None:
                res[i] = nonneg[j]
                j += 1

        return res
        