# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/longestPrefixMatches.py

# list of size len(text): arr[i] = length of match between pattern and text[i...]
# longestPrefixMatches("xaabaa", "aab") -> [0, 3, 1, 0, 2, 1]
# longestPrefixMatches([1, 2, 1, 2], [1, 2]) -> [2, 0, 2, 0]
# O(n + m) time, O(m) extra space besides the result (n = len(text), m = len(pattern))
def longestPrefixMatches(text, pattern):
    n, m = len(text), len(pattern)
    if m == 0:
        return [0] * n
    # z-function of pattern: z[i] = longest common prefix of pattern against pattern[i...]
    z = [0] * m
    z[0] = m
    l = r = 0
    for i in range(1, m):
        k = 0
        if i < r:
            k = min(r - i, z[i - l])
        while i + k < m and pattern[k] == pattern[i + k]:
            k += 1
        z[i] = k
        if i + k > r:
            l, r = i, i + k
    # the same scan over text, compared against pattern: [l, r) = text window matching pattern's start
    arr = [0] * n
    l = r = 0
    for i in range(n):
        k = 0
        if i < r:
            k = min(r - i, z[i - l])
        while k < m and i + k < n and pattern[k] == text[i + k]:
            k += 1
        arr[i] = k
        if i + k > r:
            l, r = i, i + k
    return arr
