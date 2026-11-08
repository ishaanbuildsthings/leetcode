# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/longestPalAroundEachCenter.py

# two lists of size n, from Manacher:
#   atI[i] = (l, r) of the longest palindrome centered on index i
#   atIPlusOne[i] = (l, r) of the longest palindrome centered between i and i+1, or (i+1, i) if there's none
# works on a str, list or tuple holding any items that can be compared with == (ints, chars, tuples, ...)
# atI, atIPlusOne = longestPalAroundEachCenter("abaab")
#   atI        -> [(0, 0), (0, 2), (2, 2), (3, 3), (4, 4)]
#   atIPlusOne -> [(1, 0), (2, 1), (1, 4), (4, 3), (5, 4)]
# atI, atIPlusOne = longestPalAroundEachCenter([-1, 2, -1])
#   atI        -> [(0, 0), (0, 2), (2, 2)]
#   atIPlusOne -> [(1, 0), (2, 1), (3, 2)]
# O(n) time and space
def longestPalAroundEachCenter(arrOrString):
    n = len(arrOrString)
    # odd[i] = how far the palindrome centered on i reaches, counting i itself (so at least 1)
    odd = [0] * n
    l, r = 0, -1  # the palindrome reaching furthest right so far
    for i in range(n):
        k = 1 if i > r else min(odd[l + r - i], r - i + 1)  # start from the mirrored center's answer
        while i - k >= 0 and i + k < n and arrOrString[i - k] == arrOrString[i + k]:
            k += 1
        odd[i] = k
        if i + k - 1 > r:
            l, r = i - k + 1, i + k - 1
    # even[i] = how many pairs the palindrome centered between i-1 and i has (0 if none)
    even = [0] * n
    l, r = 0, -1
    for i in range(n):
        k = 0 if i > r else min(even[l + r - i + 1], r - i + 1)
        while i - k - 1 >= 0 and i + k < n and arrOrString[i - k - 1] == arrOrString[i + k]:
            k += 1
        even[i] = k
        if i + k - 1 > r:
            l, r = i - k, i + k - 1
    atI = [(i - odd[i] + 1, i + odd[i] - 1) for i in range(n)]
    atIPlusOne = [(i + 1 - even[i + 1], i + even[i + 1]) if i + 1 < n else (i + 1, i) for i in range(n)]
    return atI, atIPlusOne
