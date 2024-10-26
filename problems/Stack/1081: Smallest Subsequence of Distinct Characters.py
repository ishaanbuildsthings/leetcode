# https://leetcode.com/problems/smallest-subsequence-of-distinct-characters/
# difficulty: medium
# tags: stack

# Problem
# Given a string s, return the
# lexicographically smallest

# subsequence
#  of s that contains all the distinct characters of s exactly once.

# Solution, O(n) time and space
# Clearly we need to add characters in order (with potential skips) since we cannot rearrange things. As we add letters to our stack, we want earlier letters to appear first, but we can only pop if the letter we pop appears again, so we maintain a count.

class Solution:
    def smallestSubsequence(self, s: str) -> str:
        stack = []
        seen = set() # letters in our stack
        counts = collections.Counter(s)
        # iterate over each letter
        for i in range(len(s)):
            # if we already have that letter, ignore it
            if s[i] in seen:
                counts[s[i]] -= 1
                continue

            # pop while we have letters, the previous letter is bigger, and we have more of it
            while len(stack) and stack[-1] > s[i] and counts[stack[-1]] > 0:
                seen.remove(stack[-1])
                stack.pop()

            stack.append(s[i])
            seen.add(s[i])
            counts[s[i]] -= 1
        return ''.join(stack)
