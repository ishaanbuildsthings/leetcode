# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/findMatchesKmp.py

# list of indices i where text[i...] matches pattern (an empty pattern matches at every i in 0..len(text))
# findMatchesKmp("ababa", "aba") -> [0, 2]
# findMatchesKmp([1, 2, 1, 2], [1, 2]) -> [0, 2]
# O(n + m) time, O(m) extra space besides the result (n = len(text), m = len(pattern))
def findMatchesKmp(text, pattern):
    n, m = len(text), len(pattern)
    if m == 0:
        return list(range(n + 1))
    pi = [0] * m
    for i in range(1, m):
        k = pi[i - 1]
        while k > 0 and pattern[i] != pattern[k]:
            k = pi[k - 1]
        if pattern[i] == pattern[k]:
            k += 1
        pi[i] = k
    res = []
    k = 0  # how much of pattern matches the text ending here
    for i in range(n):
        c = text[i]
        while k > 0 and c != pattern[k]:
            k = pi[k - 1]
        if c == pattern[k]:
            k += 1
        if k == m:
            res.append(i - m + 1)
            k = pi[k - 1]
    return res
