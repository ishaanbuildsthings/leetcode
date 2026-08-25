# https://leetcode.com/problems/queries-on-a-permutation-with-key/
# difficulty: medium

# problem
# Given the array queries of positive integers between 1 and m, you have to process all queries[i] (from i=0 to i=queries.length-1) according to the following rules:

# In the beginning, you have the permutation P=[1,2,3,...,m].
# For the current i, find the position of queries[i] in the permutation P (indexing from 0) and then move this at the beginning of the permutation P. Notice that the position of queries[i] in P is the result for queries[i].
# Return an array containing the result for the given queries.

# Solution, O(n^2) time and O(n) space, just brute force remove and insert

class Solution:
    def processQueries(self, queries: List[int], m: int) -> List[int]:
        res = []
        arr = [num for num in range(1, m + 1)]
        print(arr)
        for query in queries:
            pos = arr.index(query)
            removed = arr.pop(pos)
            arr.insert(0, removed)
            res.append(pos)
        return res
