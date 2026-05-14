# https://leetcode.com/problems/unique-substrings-with-equal-digit-frequency/
# Difficulty: Medium
# Tags: rolling hash

# Problem
# Given a digit string s, return the number of unique substrings of s where every digit appears the same number of times.

# Solution, O(n^2) time, n^3 worst case with hash collisions
# For each starting index, iterating over each ending index, accumulating a hash. Also accrue the counts of all the digits. If we get a unique hash, we (likely) have a unique string, then we can add one to the result if the amount of each character is equal.

class Solution:
    def equalDigitFrequency(self, s: str) -> int:
        MOD = (10**14) + 7
        seenHashes = set()
        result = 0
        for i in range(len(s)):
            counts = defaultdict(int) # maps a number to the amount of times it occurs
            rollHash = 0
            for j in range(i, len(s)):
                counts[s[j]] += 1
                rollHash *= 11 # 0 is counted as a unique digit, 01 != 1
                rollHash += int(s[j]) + 1
                rollHash %= MOD
                if not rollHash in seenHashes:
                    seenHashes.add(rollHash)
                    uniqueFreqs = set(counts.values())
                    if len(uniqueFreqs) == 1:
                        result += 1
        return result

