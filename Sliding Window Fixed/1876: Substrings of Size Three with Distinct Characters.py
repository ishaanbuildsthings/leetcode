# https://leetcode.com/problems/substrings-of-size-three-with-distinct-characters/description/
# difficulty: easy
# tags: sliding window fixed

# Problem
# A string is good if there are no repeated characters.

# Given a string s​​​​​, return the number of good substrings of length three in s​​​​​​.

# Note that if there are multiple occurrences of the same substring, every occurrence should be counted.

# A substring is a contiguous sequence of characters in a string.

# Solution, I kept counts so I can do fewer operations and the solution is more tenable for bigger inputs. It's slower for k=3 in machine cycles, likely. O(n) time and O(1) space

class Solution:
    def countGoodSubstrings(self, s: str) -> int:
        # this solution is more generalizable, but slower in machine cycles than brute force due to cache lookups

        # edge case
        if len(s) <= 2:
            return 0

        counts = collections.Counter(s[:3])
        have = 0
        for key in counts:
            if counts[key] > 0:
                have += 1

        res = int(have == 3)

        r = 3
        while r < len(s):
            newChar = s[r]
            counts[newChar] += 1
            if counts[newChar] == 1:
                have += 1
            lostChar = s[r - 3]
            counts[lostChar] -= 1
            if counts[lostChar] == 0:
                have -= 1
            if have == 3:
                res += 1
            r += 1

        return res