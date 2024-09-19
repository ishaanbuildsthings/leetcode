def zFunction(s):
    n = len(s)
    z = [0] * n
    l, r = 0, 0
    for i in range(1, n):
        if i <= r:
            z[i] = min(r - i + 1, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] - 1 > r:
            l, r = i, i + z[i] - 1
    return z

# returns a z function array in n+h time
def longestPrefixMatches(needle, haystack):
    concat = needle + '$' + haystack
    z = zFunction(concat)
    n = len(needle)
    result = z[len(needle) + 1:]
    return result
