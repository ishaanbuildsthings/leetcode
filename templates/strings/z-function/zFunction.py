# TEMPLATE BY github.com/ishaanbuildsthings PLEASE DO NOT USE

# Z-function: z[i] = length of the longest common prefix of the whole sequence and the suffix starting at i
# works on any indexable sequence of comparable items (string, list, tuple)


# zFunction("aabxaab") -> [7, 1, 0, 0, 3, 1, 0]   # z[0] is the full length
# zFunction([1, 2, 1, 2]) -> [4, 0, 2, 0]
# O(n) time, O(n) space
def zFunction(arrOrString):
    n = len(arrOrString)
    z = [0] * n
    if n == 0:
        return z
    z[0] = n
    l, r = 0, 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and arrOrString[z[i]] == arrOrString[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return z


# For every index of text, the length of the longest prefix of pattern that starts there.
# longestPrefixMatches("aab", "xaabaa") -> [0, 3, 1, 0, 2, 1]
# O(n + m) time
def longestPrefixMatches(pattern, text):
    m = len(pattern)
    z = zFunction(pattern + text)
    return [min(z[m + i], m) for i in range(len(text))]


# Every start index in text where pattern occurs (overlaps included), ascending.
# findMatches("aba", "ababa") -> [0, 2]
# findMatches([1, 2], [1, 2, 1, 2]) -> [0, 2]
# O(n + m) time
def findMatches(pattern, text):
    m = len(pattern)
    if m == 0:
        return list(range(len(text) + 1))
    z = zFunction(pattern + text)
    return [i for i in range(len(text)) if z[m + i] >= m]
