# https://leetcode.com/problems/remove-stones-to-minimize-the-total/description/
# Difficulty: Medium
# tags: heap

# Problem

# You are given a 0-indexed integer array piles, where piles[i] represents the number of stones in the ith pile, and an integer k. You should apply the following operation exactly k times:

# Choose any piles[i] and remove floor(piles[i] / 2) stones from it.
# Notice that you can apply the operation on the same pile more than once.

# Return the minimum possible total number of stones remaining after applying the k operations.

# floor(x) is the greatest integer that is smaller than or equal to x (i.e., rounds x down).

# Solution O(n + k log n) time, O(n) space
# Just use a heap and keep selecting the biggest. We heapify in n time and then pop k times, so O(n + k log n) time.

class Solution:
    def minStoneSum(self, piles: List[int], k: int) -> int:
        total = sum(piles)
        heap = [-1 * pile for pile in piles]
        heapq.heapify(heap)

        for i in range(k):
            biggest = heapq.heappop(heap)
            biggest *= -1
            biggestAfter = math.ceil(biggest / 2)
            loss = biggest - biggestAfter
            total -= loss
            heapq.heappush(heap, biggestAfter * -1)
        return total
