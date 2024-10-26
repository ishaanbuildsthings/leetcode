# https://leetcode.com/problems/xor-queries-of-a-subarray/description/
# difficulty: medium
# tags: prefix, range query, bit manipulation

# Problem
# You are given an array arr of positive integers. You are also given the array queries where queries[i] = [lefti, righti].

# For each query i compute the XOR of elements from lefti to righti (that is, arr[lefti] XOR arr[lefti + 1] XOR ... XOR arr[righti] ).

# Return an array answer where answer[i] is the answer to the ith query.


# Solution, O(n) time and space
class Solution:
    def xorQueries(self, arr: List[int], queries: List[List[int]]) -> List[int]:
        pf = []
        curr = 0
        for num in arr:
            curr ^= num
            pf.append(curr)

        def query(l, r):
            if l == 0:
                return pf[r]
            return pf[r] ^ pf[l - 1]

        return [query(l, r) for l, r in queries]