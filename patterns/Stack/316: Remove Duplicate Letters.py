# https://leetcode.com/problems/remove-duplicate-letters/
# difficulty: medium
# tags: stack

# Problem
# Given a string s, remove duplicate letters so that every letter appears once and only once. You must make sure your result is
# the smallest in lexicographical order
#  among all possible results.

# Solution, O(n) time and space
# Clearly we need to add characters in order (with potential skips) since we cannot rearrange things. As we add letters to our stack, we want earlier letters to appear first, but we can only pop if the letter we pop appears again, so we maintain a count.

class Solution:
    def removeDuplicateLetters(self, s: str) -> str:
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
