# https://leetcode.com/problems/assign-cookies/description/?envType=daily-question&envId=2024-01-01
# difficulty: easy
# tags: two pointer

# Problem
# Assume you are an awesome parent and want to give your children some cookies. But, you should give each child at most one cookie.

# Each child i has a greed factor g[i], which is the minimum size of a cookie that the child will be content with; and each cookie j has a size s[j]. If s[j] >= g[i], we can assign the cookie j to the child i, and the child i will be content. Your goal is to maximize the number of your content children and output the maximum number.

# Solution
# Standard two pointers

class Solution:
    def findContentChildren(self, g: List[int], s: List[int]) -> int:
        g.sort()
        s.sort()
        res = 0
        i = 0
        j = 0
        while j < len(s) and i < len(g):
            if g[i] <= s[j]:
                res += 1
                i += 1
            j += 1
        return res


        # 7 8 9 10 children

        # 5 6 7 8 cookies