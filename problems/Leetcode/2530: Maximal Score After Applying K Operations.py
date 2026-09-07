# https://leetcode.com/problems/maximal-score-after-applying-k-operations/description/
# difficulty: medium
# tags: minheap

# Solution, n + k log n time, n space

class Solution:
    def maxKelements(self, nums: List[int], k: int) -> int:
        minHeap = [num * -1 for num in nums]
        heapq.heapify(minHeap)

        score = 0

        for i in range(k):
            smallest = heapq.heappop(minHeap) * -1
            ceiling = math.ceil(smallest / 3)
            score += smallest
            heapq.heappush(minHeap, -1 * ceiling)

        return score