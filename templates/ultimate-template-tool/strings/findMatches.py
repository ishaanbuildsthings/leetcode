# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/findMatches.py

# list of indices i where text[i...] matches pattern (an empty pattern matches at every i in 0..len(text)) text and
# pattern can be any mix of str / list / tuple, holding any items that can be compared with ==
# findMatches("ababa", "aba") -> [0, 2]
# findMatches([-1, 2, -1, 2, 5], [-1, 2]) -> [0, 2]
# O(n + m) time, O(m) extra space besides the result (n = len(text), m = len(pattern))
def findMatches(text, pattern):
    n, m = len(text), len(pattern)
    if m == 0:
        return list(range(n + 1))
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
    res = []
    l = r = 0
    for i in range(n):
        k = 0
        if i < r:
            k = min(r - i, z[i - l])
        while k < m and i + k < n and pattern[k] == text[i + k]:
            k += 1
        if k == m:
            res.append(i)
        if i + k > r:
            l, r = i, i + k
    return res
