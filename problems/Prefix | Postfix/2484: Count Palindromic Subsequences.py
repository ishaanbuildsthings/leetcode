# https://leetcode.com/problems/count-palindromic-subsequences/description/
# difficulty: hard
# tags: prefix, postfix

# Problem
# Given a string of digits s, return the number of palindromic subsequences of s having length 5. Since the answer may be very large, return it modulo 109 + 7.

# Note:

# A string is palindromic if it reads the same forward and backward.
# A subsequence is a string that can be derived from another string by deleting some or no characters without changing the order of the remaining characters.

# Solution, O(n * 100) time and space, we can compute prefix and postfixes for the amount of times a subsequence of length 2 for each number from 00-99 in the pre and postfix region occur. For each index, we then query those 100 on the left and right and add to our result.

class Solution:
    def countPalindromes(self, s: str) -> int:
        prefix = []
        counts = defaultdict(int)
        counts[s[0]] += 1
        prefix.append(counts)

        for i in range(1, len(s)):
            prevCounts = prefix[i - 1]
            newCounts = prevCounts.copy()
            for oldDigit in range(10):
                oldStrDigit = str(oldDigit)
                # can help prune
                if not oldStrDigit in prevCounts:
                    continue
                newStr = oldStrDigit + str(s[i])
                newCounts[newStr] += prevCounts[oldStrDigit]
            # gain the current digit
            newCounts[s[i]] += 1
            prefix.append(newCounts)

        suffix = [None] * len(s)
        countsSuffix = defaultdict(int)
        last = len(s) - 1
        countsSuffix[s[last]] += 1
        suffix[last] = countsSuffix

        for i in range(len(s) - 2, -1, -1):
            futureCounts = suffix[i + 1]
            newCounts = futureCounts.copy()
            for futureDigit in range(10):
                futureDigitStr = str(futureDigit)
                # can help prune
                if not futureDigitStr in futureCounts:
                    continue
                prevNewDigitStr = str(s[i])
                newStr = prevNewDigitStr + futureDigitStr
                newCounts[newStr] += futureCounts[futureDigitStr]
            # gain the current digit
            newCounts[s[i]] += 1
            suffix[i] = newCounts

        res = 0
        MOD = 10**9 + 7
        for i in range(2, len(s) - 2):
            for key in prefix[i - 1]:
                if len(str(key)) == 1:
                    continue
                reversedKey = key[::-1]
                res += (prefix[i - 1][key] * suffix[i + 1][reversedKey])
                res %= MOD

        return res