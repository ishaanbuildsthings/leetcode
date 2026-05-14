# https://leetcode.com/problems/h-index/
# difficulty: medium

# Problem
# Given an array of integers citations where citations[i] is the number of citations a researcher received for their ith paper, return the researcher's h-index.

# According to the definition of h-index on Wikipedia: The h-index is defined as the maximum value of h such that the given researcher has published at least h papers that have each been cited at least h times.

# Solution
# I binary searched on the answer, you can probably use some prefix thing and also prune better. I think bucket sort makes it n+m time too.

class Solution:
    def hIndex(self, citations: List[int]) -> int:
        def isHIndexed(h):
            return sum(
                1 if citations[i] >= h else
                0
                for i in range(len(citations))
            ) >= h

        l = 0
        r = len(citations)
        while l <= r:
            m = (r + l) // 2
            res = isHIndexed(m)
            if res:
                l += 1
            else:
                r -= 1
        return r


