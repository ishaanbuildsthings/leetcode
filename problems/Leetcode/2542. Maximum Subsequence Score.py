class Solution:
    def maxScore(self, nums1: List[int], nums2: List[int], k: int) -> int:
        z = [[nums2[i], nums1[i]] for i in range(len(nums1))]
        z.sort()
        topK = [] # holds the top k-1 elements on the right
        topKSum = 0
        res = 0
        for i in range(len(z) - 1, -1, -1):
            mn, v = z[i]
            if len(topK) == k - 1:
                score = (v + topKSum) * mn
                res = max(res, score)

            topKSum += v
            heapq.heappush(topK, v)
            if len(topK) >= k:
                small = heapq.heappop(topK)
                topKSum -= small
        return res
            

