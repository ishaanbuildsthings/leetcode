# https://leetcode.com/problems/best-sightseeing-pair/
# Difficulty: Medium
# Tags: lazy heap

# Problem
# You are given an integer array values where values[i] represents the value of the ith sightseeing spot. Two sightseeing spots i and j have a distance j - i between them.

# The score of a pair (i < j) of sightseeing spots is values[i] + values[j] + i - j: the sum of the values of the sightseeing spots, minus the distance between them.

# Return the maximum score of a pair of sightseeing spots.

# Solution, O(n log n) time, O(n) space
# I had a kind of cursed solution, it was the very first thing I thought of. The easy solution is iterate over the list, tracking the best value location. It decays by 1 each time we move. Update it if the new value is better. This is O(n) time and O(1) space. Instead, what I did, was remap all the values. The rightmost value gains no benefit, the value to the left gains a benefit of 1, because it is 1 better. And so on. So [1, 2, 3] would become [3, 3, 3]. From the perspective of any number, we can view the numbers on the right. I then added the numbers to a heap, and for each number, found the best value on the right. The heap also contained indexes, so I checked the true value and updated the result. Since I want to remove from the heap, I used lazy heap removal.

class Solution:
    def maxScoreSightseeingPair(self, values: List[int]) -> int:
        # 8 2 7 5 _6_


        # _8_ 4 7 3 6
        valuesWithFactoredSpacings = [0 for _ in range(len(values))]
        count = 0
        for i in range(len(values) - 1, -1, -1):
            valuesWithFactoredSpacings[i] = values[i] + count
            count += 1

        # heap stores [val, original index]
        heap = [[-1 * val, i] for i, val in enumerate(valuesWithFactoredSpacings)]
        heapq.heapify(heap)
        lazyRemove = set() # tells us if an index needs to be lazy removed
        lazyRemove.add(0)

        res = 0
        # for each number, consider the best value it can pair with on its right
        for i in range(len(values) - 1):
            lazyRemove.add(i) # we cannot pair any numbers with the current index, since we only look to the right
            # pop all lazy removals
            while heap[0][1] in lazyRemove:
                lazyRemove.remove(heap[0][1])
                heapq.heappop(heap)

            biggestVal, j = heap[0]
            pairOnRightWithThis = values[i] + values[j] - (j - i)
            res = max(res, pairOnRightWithThis)

        return res



