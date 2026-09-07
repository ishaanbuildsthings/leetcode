# https://leetcode.com/problems/maximum-product-after-k-increments/description/
# difficulty: medium
# tags: heaps

# problem
# You are given an array of non-negative integers nums and an integer k. In one operation, you may choose any element from nums and increment it by 1.

# Return the maximum product of nums after at most k operations. Since the answer may be very large, return it modulo 109 + 7. Note that you should maximize the product before taking the modulo.


# Solution, O(n + k log n) time and O(n) space
# Always increment the smallest number as it gives the greatest proportional increase.

class Solution:
    def maximumProduct(self, nums: List[int], k: int) -> int:
        heap = [*nums]
        heapq.heapify(heap)

        for i in range(k):
            smallest = heapq.heappop(heap)
            smallest += 1
            heapq.heappush(heap, smallest)

        MOD = 10**9 + 7
        res = 1
        for num in heap:
            res *= num
            res = res % MOD
        return res

