# https://leetcode.com/problems/sum-of-beauty-of-all-substrings/
# difficulty: medium

# problem
# The beauty of a string is the difference in frequencies between the most frequent and least frequent characters.

# For example, the beauty of "abaacc" is 3 - 1 = 2.
# Given a string s, return the sum of beauty of all of its substrings.

# O(n^2) time and O(1) space (since there are a finite amount of lowercase english letters). Just enumerate substrings and maintain a count. I think technically this can be sped up if we track the max and min counts in an AVL to get log(# of unique english letters) as the constant factor.

class Solution:
    def beautySum(self, s: str) -> int:
        res = 0
        for i in range(len(s) - 1):
            counts = defaultdict(int)
            counts[s[i]] += 1
            for j in range(i + 1, len(s)):
                counts[s[j]] += 1
                maxCount = max(counts.values())
                minCount = float('inf')
                for key in counts:
                    amount = counts[key]
                    if amount > 0:
                        minCount = min(minCount, amount)
                res += maxCount - minCount
        return res
