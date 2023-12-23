# https://leetcode.com/problems/range-addition/
# Difficulty: Medium
# Tags: lazy

# Problem
# You are given an integer length and an array updates where updates[i] = [startIdxi, endIdxi, inci].

# You have an array arr of length length with all zeros, and you have some operation to apply on arr. In the ith operation, you should increment all the elements arr[startIdxi], arr[startIdxi + 1], ..., arr[endIdxi] by inci.

# Return arr after applying all the updates.

# Solution, (range + queries) time, O(range) space
# For each query, we add a +diff and -diff at the start and after the end of that range. Then we iterate through, tracking the running sum.

class Solution:
    def getModifiedArray(self, length: int, updates: List[List[int]]) -> List[int]:
        cache = [0 for _ in range(length + 1)]

        for start, end, inc in updates:
            cache[start] += inc
            cache[end + 1] -= inc

        print(cache)

        result = []
        running_sum = 0
        for i in range(length):
            diff = cache[i]
            running_sum += diff
            result.append(running_sum)

        return result

