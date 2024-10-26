# https://leetcode.com/problems/split-a-string-into-the-max-number-of-unique-substrings/description/
# difficulty: medium
# tags: backtracking

# Problem
# Given a string s, return the maximum number of unique substrings that the given string can be split into.

# You can split string s into any list of non-empty substrings, where the concatenation of the substrings forms the original string. However, you must split the substrings such that all of them are unique.

# A substring is a contiguous sequence of characters within a string.


# Solution, O(n) space not sure about time
# For each split point, try the future subproblem. Maintain which words we have seen. I checked the result if the words we have seen add to the right length but I think we could redefine the base case.
class Solution:
    def maxUniqueSplit(self, s: str) -> int:
        seen = set()

        def backtrack(i):
            # base case
            if i == len(s):
                lengthOfAllSeen = 0
                for word in list(seen):
                    lengthOfAllSeen += len(word)
                if lengthOfAllSeen == len(s):
                    return len(seen)
                else:
                    return 0

            resForThis = 0
            for splitPoint in range(i, len(s)):
                leftRegion = s[i:splitPoint + 1]
                if leftRegion in seen:
                    continue
                seen.add(leftRegion)
                maxAtThisSplit = backtrack(splitPoint + 1)
                seen.remove(leftRegion)
                resForThis = max(resForThis, maxAtThisSplit)
            return resForThis

        return backtrack(0)