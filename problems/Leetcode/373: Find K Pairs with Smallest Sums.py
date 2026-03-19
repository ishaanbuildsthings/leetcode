class Solution:
    def kSmallestPairs(self, nums1: List[int], nums2: List[int], k: int) -> List[List[int]]:
        heap = [(nums1[i] + nums2[0], i, 0) for i in range(min(len(nums1), k))]
        heapify(heap)
        res = []
        while heap and len(res) < k:
            val, i, j = heappop(heap)
            res.append([nums1[i], nums2[j]])
            if j + 1 < len(nums2):
                heappush(heap, (nums1[i] + nums2[j + 1], i, j + 1))
        return res